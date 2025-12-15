# **BEAM**

### **Beast Automated Monophyletic constraints from Newick trees**

**BEAM** is a command-line utility that automatically generates **monophyly (MRCA) constraint priors** for **BEAST 2** XML analyses from a Newick tree.
It creates valid `<distribution>` blocks using `MRCAPrior`, optionally inserts them directly into an existing BEAST XML file, and ensures all new priors are properly logged.

BEAMX removes the need for manual MRCA specification in BEAUti and guarantees consistency between tree topology, priors, and loggers.

[!NOTE] It does not create a age prior distribution, but it can be added opening the XML file in BEUTI or manually edditing the XML 

---

## 🚀 Features

* Automatically derives **all internal clades** from a Newick tree
* Generates BEAST-compatible **`MRCAPrior`** XML blocks
* Names constraints consistently (`mrca_01`, `mrca_02`, …, `root`)
* Correctly inserts priors into:

  * `<distribution id="prior">`
  * `<logger id="tracelog">`
* Safe XML parsing (no regex or string hacks)
* Produces **copy-paste insertion blocks** when no XML file is supplied

---

## 📦 Installation

```bash
git clone https://github.com/ghfazevedo/beam
cd beam
pip install .
```


### Requirements (should be installed automatically with pip install

* Python ≥ 3.8
* `ete3`


### 🧠 Notes specific to BEAST users

- BEAM **does not depend on BEAST being installed**
- It only generates/modifies XML
- Fully compatible with BEAST 2.x XML


---

## 🧠 Concept

In BEAST, monophyly constraints are enforced using **MRCA priors**.
Given a rooted Newick tree, BEAMX:

1. Identifies every internal node (clade)
2. Extracts its descendant taxa
3. Generates a corresponding `MRCAPrior`
4. Ensures the full taxon set is labeled as `root`

This ensures **topological consistency** between the supplied tree and the BEAST prior structure.

---

## 🔧 Usage

```bash
beamx -t TREE.nwk -spec SPEC -tn TREE_NAME [-xml analysis.xml]
```

### Required arguments

| Flag    | Description                                                           |
| ------- | --------------------------------------------------------------------- |
| `-t`    | Input Newick tree                                                     |
| `-spec` | BEAST prior specification (e.g. `beast.math.distributions.MRCAPrior`) |
| `-tn`   | Tree reference name used in the BEAST XML (e.g. `Tree.t:Species`)     |

### Optional arguments

| Flag   | Description                                |
| ------ | ------------------------------------------ |
| `-xml` | Existing BEAST XML file to modify in place |

---

## 🧪 Example

### Input tree (`tree.nwk`)

```text
(((A,B),C),D);
```

### Command

```bash
beamx \
  -t tree.nwk \
  -spec beast.math.distributions.MRCAPrior \
  -tn Tree.t:Species \
  -xml analysis.xml
```

---

## 🧾 Behavior with `-xml`

If an XML file is provided, BEAMX will:

### 1️⃣ Append MRCA priors to

```xml
<distribution id="prior" spec="util.CompoundDistribution">
    ...
</distribution>
```

### 2️⃣ Append loggers to

```xml
<logger id="tracelog" spec="Logger">
    ...
</logger>
```

Example additions:

```xml
<distribution id="mrca_01.prior" spec="beast.math.distributions.MRCAPrior" tree="@Tree.t:Species">
    <taxonset id="mrca_01" spec="TaxonSet">
        <taxon idref="A"/>
        <taxon idref="B"/>
    </taxonset>
</distribution>

<log idref="mrca_01.prior"/>
```

All changes preserve existing XML structure and ordering.

---

## 🧾 Behavior without `-xml`

If no XML file is provided, BEAMX writes **`taxonset.xml`**, containing **commented insertion blocks**:

```xml
<!-- THE UNCOMENTED BLOCK SHOULD BE BETWEEN THE COMENTED BLOCKS IN YOUR XML FILE -->
<!--distribution id="prior" spec="util.CompoundDistribution" -->
    <distribution id="mrca_01.prior" ...>
        ...
    </distribution>
<!--/distribution>
     <distribution id="vectorPrior" ...> -->

<!-- THE UNCOMENTED BLOCK SHOULD BE BETWEEN THE COMENTED BLOCKS IN YOUR XML FILE -->
<!--logger id="tracelog" spec="Logger" ... -->
    <log idref="mrca_01.prior"/>
<!--/logger-->
```

This allows safe manual integration into BEAUti-generated XML files.


[!NOTE] It does not create a age prior distribution, but it can be added opening the XML file in BEUTI or manually edditing the XML 

---

## 🏷 Naming Convention

| Constraint              | Description                    |
| ----------------------- | ------------------------------ |
| `mrca_01`, `mrca_02`, … | Internal monophyletic clades   |
| `root`                  | Constraint containing all taxa |

Each prior is logged using:

```xml
<log idref="mrca_XX.prior"/>
```

---

## 📚 Recommended Citation (example)

> Monophyly constraints were generated automatically using **BEAM** (https://github.com/ghfazevedo/beam), a BEAST XML utility that derives MRCA priors directly from Newick trees.

(You may adapt this wording to your Methods section.)

---

## 🛠 License

MIT License (or specify your preferred license)

---

## 👤 Author

Guilherme Azevedo


## Disclaimer

Code and README file created with AI assitance based on a pseudocode.