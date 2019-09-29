# Itemise Git History

An alternative view of the RISC OS Git History.

## Requirements

Python 3 and pyGit2 are required, on Debian and derivatives these can be installed by installing the package `python3-pygit2`. Unless and until someone ports these programs it will not run on RISC OS. It has been tested on Debian GNU/Linux but should run on other operating systems.

## igh_mirror

`igh_mirror` will download and process the RISC OS Open Git repositories to add a branch, `all-commits`, to all the `Products` repositories containing a commit for every submodule

| Option   | Default                          | Action                                                                                                       |
| ---      | ---                              | ---                                                                                                          |
| --tree   | `repositories`                   | Directory where repositories will downloaded to and processed in.                                            |
| --remote | `https://gitlab.riscosopen.org/` | Location to download from.                                                                                   |
| --update |                                  | If provided repositories will be updated from upstream, otherwise only missing repositories will be fetched. |

If any none option arguments are provided these will be used as a list of Product repositories to process, any trailing `.git` should be included, for example `Products/Disc.git` for the `Disc` product. Otherwise a built-in list will be used.

## igh_unified

`igh_unified` will download and process the RISC OS Open Git repositories, merging them into a single repository, which must already exist. For every product repository an all commits branch will be created like `igh_mirror`, and unified versions of the product branches will be created with submodules replaced by their contents. Every branch based upon a unified branch, will be split apart into super-project and submodule branches.

| Option   | Default                          | Action                                                                                                   |
| ---      | ---                              | ---                                                                                                      |
| --repo   | `unified`                        | Existing repository where repositories will downloaded to and processed.                                 |
| --remote | `https://gitlab.riscosopen.org/` | Location to download from.                                                                               |
| --update |                                  | If provided branches will be updated from upstream, otherwise only missing repositories will be fetched. |

As with `igh_mirror`, if any none option arguments are provided these will be used as a list of Product repositories to process, otherwise the built-in list will be used.
