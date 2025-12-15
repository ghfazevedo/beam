#!/usr/bin/env python3
import argparse
import sys
from ete3 import Tree
import xml.etree.ElementTree as ET

# ---------------------------
# Tree utilities
# ---------------------------

def collect_taxa(node):
    return sorted(leaf.name for leaf in node.iter_leaves())

def build_mrca_blocks(tree, spec, treename):
    blocks = []
    log_ids = []

    counter = 1
    for node in tree.traverse():
        if node.is_leaf():
            continue

        taxa = collect_taxa(node)

        if node.is_root():
            base_id = "root"
        else:
            base_id = f"mrca_{counter:02d}"
            counter += 1

        dist_id = f"{base_id}.prior"
        log_ids.append(dist_id)

        dist = ET.Element(
            "distribution",
            {
                "id": dist_id,
                "spec": spec,
				"monophyletic": "true", 
                "tree": f"@{treename}"
            }
        )

        taxonset = ET.SubElement(
            dist,
            "taxonset",
            {"id": base_id, "spec": "TaxonSet"}
        )

        for tax in taxa:
            ET.SubElement(taxonset, "taxon", {"idref": tax})

        blocks.append(dist)

    return blocks, log_ids
    
def label_internal_nodes(tree):
    """
    Label internal nodes with MRCA IDs matching build_mrca_blocks().
    Modifies the tree in place.
    """
    counter = 1

    for node in tree.traverse():
        if node.is_leaf():
            continue

        if node.is_root():
            node.name = "root"
        else:
            node.name = f"mrca_{counter:02d}"
            counter += 1


# ---------------------------
# XML insertion helpers
# ---------------------------

def find_element(root, tag, attrib_key, attrib_value):
    for el in root.iter(tag):
        if el.attrib.get(attrib_key) == attrib_value:
            return el
    return None

# ---------------------------
# Main
# ---------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate BEAST MRCA taxonset priors from a Newick tree."
    )
    parser.add_argument("-t", "--tree", required=True, help="Input Newick tree file")
    parser.add_argument("-spec", default="beast.math.distributions.MRCAPrior", help="BEAST prior specification (default: beast.math.distributions.MRCAPrior). It may change according to version and model used. This is for species tree in Starbeast3")
    parser.add_argument("-tn", "--treename", default="Tree.t:Species", help="Tree ID reference in BEAST XML (default: Tree.t:Species). It may change according to version and model used. This is for species tree in Starbeast3")
    parser.add_argument("-xml", "--xmlfile", help="Existing BEAST XML to modify")
    args = parser.parse_args()

    tree = Tree(args.tree, format=1)
    
    # Label internal nodes and write annotated Newick
    label_internal_nodes(tree)
    tree_out = args.tree.rsplit(".", 1)[0] + "_nodenames.nwck"
    tree.write(outfile=tree_out, format=1)
    
    mrca_blocks, log_ids = build_mrca_blocks(tree, args.spec, args.treename)

    # ------------------------------------------------------------
    # CASE 1: XML FILE PROVIDED → MODIFY IT
    # ------------------------------------------------------------
    if args.xmlfile:
        xml_tree = ET.parse(args.xmlfile)
        root = xml_tree.getroot()

        prior_block = find_element(
            root, "distribution", "id", "prior"
        )
        if prior_block is None:
            sys.exit("ERROR: <distribution id='prior'> not found")

        for block in mrca_blocks:
            prior_block.append(block)

        tracelog = find_element(
            root, "logger", "id", "tracelog"
        )
        if tracelog is None:
            sys.exit("ERROR: <logger id='tracelog'> not found")

        for lid in log_ids:
            ET.SubElement(tracelog, "log", {"idref": lid})

        xml_tree.write(args.xmlfile, encoding="utf-8", xml_declaration=True)
        print(f"Updated XML written to: {args.xmlfile}")
        return

    # ------------------------------------------------------------
    # CASE 2: NO XML FILE → WRITE COMMENTED INSERTION BLOCKS
    # ------------------------------------------------------------
    out = []

    out.append("<!-- THE UNCOMENTED BLOCK SHOULD BE BETWEEN THE COMENTED BLOCKS IN YOUR XML FILE -->")
    out.append("<!--distribution id=\"prior\" spec=\"util.CompoundDistribution\" -->")

    for block in mrca_blocks:
        out.append(ET.tostring(block, encoding="unicode"))

    out.append("<!--/distribution>")
    out.append("    <distribution id=\"vectorPrior\" spec=\"util.CompoundDistribution\">")
    out.append("        ...")
    out.append("    </distribution -->\n")

    out.append("<!-- THE UNCOMENTED BLOCK SHOULD BE BETWEEN THE COMENTED BLOCKS IN YOUR XML FILE -->")
    out.append("<!--logger id=\"tracelog\" spec=\"Logger\" fileName=\"beast.log\" logEvery=\"10000\" model=\"@posterior\" sort=\"smart\" -->")

    for lid in log_ids:
        out.append(f"    <log idref=\"{lid}\"/>")

    out.append("<!--/logger-->")

    with open("taxonset.xml", "w") as fh:
        fh.write("\n".join(out))

    print("Created taxonset.xml")

if __name__ == "__main__":
    main()
