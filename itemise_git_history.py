# Copyright 2018, 2019 Timothy Baldwin
# Tables possibly copyright RISC OS Developments, RISC OS Open and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import heapq
import os
import posixpath
import re
import urllib.request
import urllib.parse
import json
import pprint
import collections
import datetime
import pdb

import pygit2

all_products = (
  "Products/BCM2835.git",
  "Products/BCM2835Pico.git",
  "Products/Batch1to6.git",
  "Products/BonusBin.git",
  "Products/BuildHost.git",
  "Products/Disc.git",
  "Products/IOMDHAL.git",
  "Products/OMAP3.git",
  "Products/OMAP4.git",
  "Products/OMAP5.git",
  "Products/PlingSystem.git",
  "Products/S3C.git",
  "Products/Titanium.git",
  "Products/Tungsten.git",
  "Products/iMx6.git",
  "Products/All.git"
)

path_map = {
  # This dict is derived from a table provided by RISC OS Open Limited
  "RiscOS/Sources/Apps/Diversions/MineHuntBin":                          "RiscOS/Sources/Apps/Diversions/MineHunt",
  "RiscOS/Sources/Apps/EditApp":                                         "RiscOS/Sources/Apps/Edit",
  "RiscOS/Sources/Apps/SquashApp":                                       "RiscOS/Sources/Apps/Squash",
  "RiscOS/Sources/FileSys/ADFS/ADFS4":                                   "RiscOS/Sources/FileSys/ADFS/ADFS",
  "RiscOS/Sources/HAL/HAL_BCM2835":                                      "RiscOS/Sources/HAL/BCM2835",
  "RiscOS/Sources/HAL/HAL_iMx6":                                         "RiscOS/Sources/HAL/iMx6",
  "RiscOS/Sources/HAL/HAL_IOMD":                                         "RiscOS/Sources/HAL/IOMD",
  "RiscOS/Sources/HAL/HAL_OMAP3":                                        "RiscOS/Sources/HAL/OMAP3",
  "RiscOS/Sources/HAL/HAL_OMAP4":                                        "RiscOS/Sources/HAL/OMAP4",
  "RiscOS/Sources/HAL/HAL_OMAP5":                                        "RiscOS/Sources/HAL/OMAP5",
  "RiscOS/Sources/HAL/HAL_PsionNB2":                                     "RiscOS/Sources/HAL/PsionNB2",
  "RiscOS/Sources/HAL/HAL_S3C2440":                                      "RiscOS/Sources/HAL/S3C2440",
  "RiscOS/Sources/HAL/HAL_S3C6410":                                      "RiscOS/Sources/HAL/S3C6410",
  "RiscOS/Sources/HAL/HAL_Titanium":                                     "RiscOS/Sources/HAL/Titanium",
  "RiscOS/Sources/HAL/HAL_Tungsten":                                     "RiscOS/Sources/HAL/Tungsten",
  "RiscOS/Sources/HWSupport/CD/CDFSSoftSCSI":                            "RiscOS/Sources/HWSupport/CD/SCSI",
  "RiscOS/Sources/HWSupport/FPASCBlob":                                  "RiscOS/Sources/HWSupport/FPASC",
  "RiscOS/Sources/HWSupport/USB/Test/TestProtoUComb":                    "RiscOS/Sources/HWSupport/USB/Test/ProtoUComb",
  "RiscOS/Sources/HWSupport/USB/Test/TestProtoUKey":                     "RiscOS/Sources/HWSupport/USB/Test/ProtoUKey",
  "RiscOS/Sources/HWSupport/USB/Test/TestProtoUMouse":                   "RiscOS/Sources/HWSupport/USB/Test/ProtoUMouse",
  "RiscOS/Sources/Internat/Territory/TerritoryManager":                  "RiscOS/Sources/Internat/Territory/Manager",
  "RiscOS/Sources/Internat/Territory/TerritoryModule":                   "RiscOS/Sources/Internat/Territory/Module",
  "RiscOS/Sources/Lib/ConfigLib":                                        "RiscOS/Sources/Lib/Configure",
  "RiscOS/Sources/Lib/Email/EmailCommon":                                "RiscOS/Sources/Lib/Email/Common",
  "RiscOS/Sources/Lib/UnicodeLib":                                       "RiscOS/Sources/Lib/Unicode",
  "RiscOS/Sources/Networking/AUN/Access/ShareFSBlob":                    "RiscOS/Sources/Networking/AUN/Access/ShareFS",
  "RiscOS/Sources/Networking/AUN/Apps/AccessPlus":                       "RiscOS/Sources/Networking/AUN/Apps/Access+",
  "RiscOS/Sources/Networking/AUN/MManagerBlob":                          "RiscOS/Sources/Networking/AUN/MManager",
  "RiscOS/Sources/Networking/Fetchers/Fetchers":                         "RiscOS/Sources/Networking/Fetchers/Common",
  "RiscOS/Sources/Networking/Fetchers/GenericFetcher":                   "RiscOS/Sources/Networking/Fetchers/Generic",
  "RiscOS/Sources/Networking/MimeMapBlob":                               "RiscOS/Sources/Networking/MimeMap",
  "RiscOS/Sources/Networking/Omni/Protocols/OmniAccess":                 "RiscOS/Sources/Networking/Omni/Protocols/Access",
  "RiscOS/Sources/Networking/Omni/Protocols/OmniLanManFS":               "RiscOS/Sources/Networking/Omni/Protocols/LanManFS",
  "RiscOS/Sources/Networking/Omni/Protocols/OmniNetFiler":               "RiscOS/Sources/Networking/Omni/Protocols/NetFiler",
  "RiscOS/Sources/Networking/ResolverBlob":                              "RiscOS/Sources/Networking/Resolver",
  "RiscOS/Sources/Printing/PrinterManager":                              "RiscOS/Sources/Printing/Manager",
  "RiscOS/Sources/Programmer/DDTHdr":                                    "RiscOS/Sources/Programmer/DDT",
  "RiscOS/Sources/Programmer/SquashBlob":                                "RiscOS/Sources/Programmer/Squash",
  "RiscOS/Sources/Programmer/ZLibMod":                                   "RiscOS/Sources/Programmer/ZLib",
  "RiscOS/Sources/SystemRes/DesktopBoot":                                "RiscOS/Sources/SystemRes/Boot",
  "RiscOS/Sources/SystemRes/Configure2/Config2Main":                     "RiscOS/Sources/SystemRes/Configure2/Main",
  "RiscOS/Sources/SystemRes/Configure2/PlugIns/Config2PluginBoot":       "RiscOS/Sources/SystemRes/Configure2/PlugIns/Boot",
  "RiscOS/Sources/SystemRes/Configure2/PlugIns/Config2PluginBootxxxx":   "RiscOS/Sources/SystemRes/Configure2/PlugIns/Bootxxxx",
  "RiscOS/Sources/SystemRes/Configure2/PlugIns/Config2PluginxxxxMerge":  "RiscOS/Sources/SystemRes/Configure2/PlugIns/xxxxMerge",
  "RiscOS/Sources/SystemRes/InetRes":                                    "RiscOS/Sources/SystemRes/Internet",
  "RiscOS/Sources/SystemRes/PatchApp":                                   "RiscOS/Sources/SystemRes/Patch",
  "RiscOS/Sources/Video/UserI/ScrSavers/DeskBall":                       "RiscOS/Sources/ThirdParty/7thsoftware/Video/UserI/ScrSavers/DeskBall",
  "RiscOS/Sources/Video/UserI/ScrSavers/Rain":                           "RiscOS/Sources/ThirdParty/7thsoftware/Video/UserI/ScrSavers/Rain",
  "RiscOS/Sources/Video/UserI/ScrSavers/Random":                         "RiscOS/Sources/ThirdParty/7thsoftware/Video/UserI/ScrSavers/Random",
  "RiscOS/Sources/Video/UserI/ScrSavers/Shred":                          "RiscOS/Sources/ThirdParty/7thsoftware/Video/UserI/ScrSavers/Shred",
  "RiscOS/Sources/Video/UserI/ScrSavers/Snow":                           "RiscOS/Sources/ThirdParty/7thsoftware/Video/UserI/ScrSavers/Snow",
  "RiscOS/Sources/Video/UserI/ScrSavers/SprBounce":                      "RiscOS/Sources/ThirdParty/7thsoftware/Video/UserI/ScrSavers/SprBounce",
  "RiscOS/Sources/Lib/Desk":                                             "RiscOS/Sources/ThirdParty/Desk/Lib/Desk",
  "RiscOS/Sources/Apps/SparkFSBin":                                      "RiscOS/Sources/ThirdParty/DPilling/Apps/SparkFS",
  "RiscOS/Sources/Lib/DThreads":                                         "RiscOS/Sources/ThirdParty/Endurance/Lib/DThreads",
  "RiscOS/Sources/Lib/DDTLib":                                           "RiscOS/Sources/ThirdParty/JSmith/Lib/DDTLib",
  "RiscOS/Sources/Lib/Trace":                                            "RiscOS/Sources/ThirdParty/JSmith/Lib/Trace",
  "RiscOS/Sources/Lib/Wild":                                             "RiscOS/Sources/ThirdParty/JSmith/Lib/Wild",
  "RiscOS/Sources/Lib/OSLib":                                            "RiscOS/Sources/ThirdParty/OSLib/Lib/OSLib",
  "RiscOS/Sources/Audio/QTheMusic":                                      "RiscOS/Sources/ThirdParty/SHarrison/Audio/QTheMusic",
  "RiscOS/Sources/HWSupport/GPIO":                                       "RiscOS/Sources/ThirdParty/TankStage/HWSupport/GPIO",
  "RiscOS/Sources/Utilities/GPIOConfig":                                 "RiscOS/Sources/ThirdParty/TankStage/Utilities/GPIOConfig",
  "RiscOS/Sources/Apps/COMCentre":                                       "RiscOS/Sources/ThirdParty/TMilius/Apps/COMCentre",
  "RiscOS/Sources/HWSupport/InOutput/FTDI":                              "RiscOS/Sources/ThirdParty/TMilius/HWSupport/InOutput/FTDI",
  "RiscOS/Sources/HWSupport/InOutput/USBDevSwp":                         "RiscOS/Sources/ThirdParty/TMilius/HWSupport/InOutput/USBDevSwp",
  "RiscOS/Sources/HWSupport/InOutput/USBSDvEmu":                         "RiscOS/Sources/ThirdParty/TMilius/HWSupport/InOutput/USBSDvEmu",
  "RiscOS/Sources/HWSupport/Input/TchScrn":                              "RiscOS/Sources/ThirdParty/TMilius/HWSupport/Input/TchScrn",
  "RiscOS/Sources/HWSupport/USB/USBDriver":                              "RiscOS/Sources/HWSupport/USB/NetBSD",
  "RiscOS/Sources/Toolbox/tboxlib":                                      "RiscOS/Sources/Toolbox/Common",
  "RiscOS/Sources/Toolbox/ToolboxDocs":                                  "RiscOS/Sources/Toolbox/Docs",
  "RiscOS/Sources/Toolbox/ToolboxLib":                                   "RiscOS/Sources/Toolbox/Libs",
  "RiscOS/Sources/Utilities/Patches/PatchesPatch":                       "RiscOS/Sources/Utilities/Patches/Patch",
  "RiscOS/Sources/Video/HWSupport/GC320VideoBlob":                       "RiscOS/Sources/Video/HWSupport/GC320Video",
  "RiscOS/Sources/Video/HWSupport/OMAPHDMIBlob":                         "RiscOS/Sources/Video/HWSupport/OMAPHDMI",
  "RiscOS/Sources/Video/Render/DrawMod":                                 "RiscOS/Sources/Video/Render/Draw",
  "RiscOS/Sources/Video/Render/Fonts/FontManager":                       "RiscOS/Sources/Video/Render/Fonts/Manager"
}

rearrange_date = datetime.datetime(2011, 3, 17, 19, 32).timestamp()
cvs_end_date = datetime.datetime(2019, 5, 1).timestamp()

def dict_factory(*x):
    return collections.defaultdict(dict_factory, *x)

def load_push_cache():
    global push_cache
    try:
        with open(push_cache_file, "rb") as f:
            push_cache = json.load(f, object_hook=dict_factory)
    except FileNotFoundError:
        push_cache = dict_factory()

def save_push_cache():
    fn = push_cache_file + ".tmp"
    with open(fn, "w") as f:
        json.dump(push_cache, f)
    os.rename(fn, push_cache_file)

def get_pushes(path, update):
    d = push_cache[path]
    branches = d["branches"]
    if update:
        latest = d.get("latest", "2019-05-01")
        url = "https://gitlab.riscosopen.org/api/v4/projects/" + urllib.parse.quote(path, safe="") +"/events?action=pushed&after=" + latest
        print("Fetching " + url)
        with urllib.request.urlopen(url) as f:
            j = json.load(f)
            pprint.pprint(j)

        for event in j:
            push_data = event["push_data"]
            if push_data["ref_type"] == "branch":
                date = event["created_at"]
                branches[push_data["ref"]][push_data["commit_from"]] = date
                if date > latest:
                    latest = date

        d["latest"] = latest
    return branches

class Commit:
    def __lt__(a, b):
        return (a.committer.time, a.oid) < (b.committer.time, b.oid)
    def __iter__(c):
        yield c
        while c.parents:
            c = c.parents[0]
            yield c

class CommitPtr:
    def __init__(self, l, path, name):
        self.list = l
        self.path = path
        self.name = name
        self.index = 0
    def __lt__(a, b):
        return a.list[a.index] < b.list[b.index]
    def get(self):
        return self.list[self.index]

def load_repository(name, repo, update=True, prefix="refs/heads/"):

    def load_commit(oid):
        c = commits.get(oid)
        if c is not None:
            return c
        c1 = repo[oid]
        if isinstance(c1, pygit2.Tag):
            c = load_commit(c1.target)
        else:
            c = Commit()
            c.oid = oid
            c.author = c1.author
            c.committer = c1.committer
            c.message = c1.message.strip()
            c.tree_id = c1.tree_id
            c.parents = [load_commit(i) for i in c1.parent_ids]
        commits[oid] = c
        return c

    branches = get_pushes(name, update)

    commits = dict()
    refs = dict()

    for ref1 in repo.listall_references():
        if ref1.startswith(prefix):
            ref = repo.lookup_reference(ref1)
            if ref.type == pygit2.GIT_REF_OID:
                ref1 = ref1[len(prefix):]
                commit_list = list(load_commit(ref.target))
                commit_dict = branches[ref1]
                min_time = 0
                for commit in reversed(commit_list):
                    if commit.committer.time < min_time:
                        commit.committer = pygit2.Signature(email=commit.committer.email, name=commit.committer.name, time=min_time)
                    new_time = commit_dict.get(str(commit.oid))
                    if new_time is not None:
                        new_time = int(datetime.datetime.strptime(new_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
                        if new_time > min_time:
                            min_time = new_time
                refs[ref1] = commit_list

    return refs


__parse_modules_re = re.compile(
    r"^\[[ \t]*submodule[ \t]+\"([^\n]*)\"[ \t]*]\n(?:[ \t]+path *= *(\S*)\n|[ \t]+branch *= *(\S*)\n|[ \t]+url *= *(\S*)\n|[ \t]+[^\n]*\n)*", re.MULTILINE)

def convert(repo, branch, product_name, get_branch):

    def add_module(module):
        index.add(pygit2.IndexEntry(module.path, module.get().oid, pygit2.GIT_FILEMODE_COMMIT))

    # Find first commit in source branch
    # and create child
    current = CommitPtr(branch, "", product_name)
    current.index = len(current.list) - 1
    heap = [current]
    parents = []

    while heap:

        current = heap[0]
        print(product_name, datetime.datetime.utcfromtimestamp(current.get().committer.time))

        if current.path == "":
            parents.append(current.get().oid)
            heap = []
            index = pygit2.Index()
            index.read_tree(repo[current.get().tree_id])

            # Read modules
            blob_id = index[".gitmodules"].id

            text = repo[blob_id].read_raw().decode("latin1")
            modules = ""
            for name, path, tag, url in sorted(x.groups() for x in __parse_modules_re.finditer(text)):

                # Load tag or branch
                if tag is None:
                    tag = "master"

                module = CommitPtr(get_branch(name, url, tag), path, posixpath.basename(path))

                # Find latest commit before current
                while module.index < len(module.list) and module > current:
                    module.index += 1

                if module.index < len(module.list):
                    add_module(module)

                # Add symbolic links for moved components
                link = path_map.get(module.path)
                if link is not None and current.get().committer.time < rearrange_date:
                    index.add(pygit2.IndexEntry(link, repo.create_blob(posixpath.relpath(module.path, posixpath.dirname(link))), pygit2.GIT_FILEMODE_LINK))

                module.index -= 1
                if module.index >= 0:
                    heapq.heappush(heap, module)

        else: # current_path == ""
            heapq.heappop(heap)
            add_module(current)

        parents = [repo.create_commit(
            None,
            current.get().author,
            current.get().committer,
            current.name + ": " + current.get().message,
            index.write_tree(repo),
            parents)]

        current.index -= 1
        if current.index >= 0:
            heapq.heappush(heap, current)

    print(product_name + " conversion finished")
    return parents[0]


def init_remote(repo, name, url):
    remote = repo.remotes.create("origin", url, "+refs/*:refs/*")
    repo.config["remote.origin.mirror"] = True
    return remote

def open_repository(source, path, update=False):
    if os.path.isdir(path):
        r = pygit2.Repository(path)
        if update:
            try:
                remote = r.remotes["origin"]
            except KeyError:
                pass
            else:
                print("Fetching", source)
                remote.fetch(refspecs=remote.fetch_refspecs)
    else:
        print("Cloning", source)
        r = pygit2.clone_repository(source, path, bare=True, remote=init_remote)
    return r
