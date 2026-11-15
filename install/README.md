# C4 test-branch installer

User instructions and warning: [繁體中文安裝指南](../docs/C4_TEST_INSTALL_zh-TW.md).

`c4-test` is an AArch64 ELF installer for comma four / MICI. It clones:

- Repository: `https://github.com/FANHAOHSIANG/openpilot-carrot.git`
- Branch: `test/carrot-wip-upstream-20261104`

It follows that branch at installation time. It does not pin the vehicle software to the commit recorded in the manifest. It is not an Android APK and has not been installed or boot-tested on a physical C4.

## Provenance and modifications

The base was downloaded from comma's `https://installer.comma.ai/commaai/nightly-dev` with `User-Agent: AGNOSSetup-19.8` and `X-openpilot-device-type: mici`. The base SHA-256 is fixed in `prepare_installer.py` and `c4-test.json`.

The preparer changes four literal strings: the padded Git URL, padded branch, unused cache marker, and progress title (`TEST BRANCH`). The stock `/data/.openpilot_cache` marker must not cause a fetch from an unrelated retained origin. This build uses `/data/.cb1104_no_cache`, a marker that this installer does not create. Do not create that marker manually. The ordinary path therefore performs a fresh clone of the explicitly named repository.

Length, ELF architecture, exact base hash, single matching literals, read-only data section locations and unchanged executable sections are checked before writing. No vehicle software is run by the preparer. The ELF build-id still identifies the upstream build; use the published SHA-256 to identify this modified file.

Reference source for the installer structure: [comma installer](https://github.com/commaai/openpilot/blob/edde587a77847261fada475a15831b42732b1459/openpilot/selfdrive/ui/installer/installer.cc). This is a source reference, not a claim that the endpoint's prebuilt binary has been reproducibly matched to that source commit. The base's code is unchanged. Original copyright and license: [LICENSE.comma](LICENSE.comma); upstream components retain their own licenses.

## Reproduce

Download the base without executing it, retaining the headers above. Then:

```sh
python3 install/prepare_installer.py /path/to/verified-comma-mici-installer install/c4-test
```

If the endpoint changes its bytes, the preparer refuses them. Review the new base and validation before changing the fixed hash; do not silently accept a different installer. Files `c4-test.json` and `c4-test.sha256` describe the result.

This publishes an experimental install path. Real C4 installation, AGNOS compatibility, first boot, and vehicle acceptance remain unverified. Do not describe an HTTP download or an offline ELF check as a successful device installation.
