# File organiser demo

A small Python command-line demonstration that groups files by extension while preserving their original subfolders. It previews the work before copying and verifies copied content with SHA-256.

Python 3.10 or newer. Standard library only. AI-assisted development; local behavior tests have been run.

## Inspect and run the demonstration

Review `organize_files.py` first. From this directory, preview the included synthetic files:

```text
python organize_files.py sample-input organised-copy
```

To perform the copy:

```text
python organize_files.py sample-input organised-copy --copy
```

Use a new output directory for each copy run. An existing output folder is deliberately rejected. The source directory stays in place.

## Example

The included filenames exercise Chinese Unicode paths:

```text
sample-input/                 organised-copy/
  客户甲/订单.TXT                txt/客户甲/订单.TXT
  客户乙/订单.TXT                txt/客户乙/订单.TXT
  README                        no-extension/README
```

The two same-named files contain different synthetic text. Both are retained in separate client folders.

## Verification

```text
python -m unittest -v test_organize_files.py
```

Four behavior checks cover Unicode and duplicate basenames, retaining originals, rejecting existing or nested output directories, detecting changed inputs, and rejecting modified destination entries.

## Scope and limits

- Intended for modest, trusted local folders. Keep the input unchanged while the program runs.
- Links are rejected when encountered; do not use this as a defense against malicious concurrent filesystem changes.
- Hashing currently reads each file into memory. Very large files require a streaming implementation.
- A failed or interrupted copy may leave a partial output folder. Original files remain; inspect the result and choose a new output folder before retrying.
- This is a self-created demonstration, not a customer case study or a guarantee of suitability for your data.

## Licensing status

No general reuse license has been selected for this repository. Public visibility does not mean this code is offered under an open-source license. GitHub's platform rights to view and fork public repositories are unaffected.

## A different workflow?

[Describe a custom file-processing task to Small Workflow Lab](https://small-workflow-lab.bubbly-lark-0249.chatgpt.site/?source=github-file-organizer-demo). This optional service concerns separately scoped custom work; sending an enquiry does not place an order. Please mention this repository if it led you there.
