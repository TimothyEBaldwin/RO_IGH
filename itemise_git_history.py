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
import datetime

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

redate_map = {
  "3006b4492c7877b853a00eab339dda2033479396": "2019-05-11T04:57:42.413Z", # Products/BonusBin
  "b4ce2a51605719cd3724d9ad5d5383e16f169441": "2019-05-11T04:57:55.955Z", # Products/Disc
  "a0aa4e580bca75b9b084134dfcf96f031eb96209": "2019-05-11T04:58:20.710Z", # Products/PlingSystem
  "a8101de3ad4f3d531367542bf48449d5cf00c368": "2019-05-11T09:45:33.349Z", # RiscOS/Tools/Sources/GNU/bison
  "36ed95f7a6b73d7bf24d34bfe8fcdfc824c08114": "2019-05-11T09:50:41.584Z", # RiscOS/Sources/Utilities/Connector
  "b255700bdc7a9fe05c26282f7ae3afd039be5f22": "2019-05-11T10:00:38.154Z", # RiscOS/Tools/Sources/GNU/defmod
  "9894f4371bb02a3c36dea387614a03ae385ae543": "2019-05-11T10:01:58.431Z", # RiscOS/Sources/Lib/Desk
  "4985ff76f698cbca6f220784a82e9f09ec21a424": "2019-05-11T10:03:19.514Z", # RiscOS/Sources/HWSupport/USB/Controllers/EHCIDriver
  "cfb2e2913277fdaa3e50c845f406e4618584ee4b": "2019-05-11T10:03:27.546Z", # RiscOS/Sources/Networking/Ethernet/EtherB
  "6b3f215263ec6f2ce50c79d40bab624b13b8e8c7": "2019-05-11T10:03:36.043Z", # RiscOS/Sources/Networking/Ethernet/EtherCPSW
  "959eaa618bc134fc644cf46802401ad01477e7d3": "2019-05-11T10:04:07.101Z", # RiscOS/Sources/Networking/Ethernet/EtherY
  "cc29259315f7961350ff23005e8b1561b42ba496": "2019-05-11T10:05:05.182Z", # RiscOS/Tools/Sources/GNU/flex
  "8dfe324391512209ca249afe02fb463d0378d646": "2019-05-11T10:05:19.488Z", # RiscOS/Tools/Sources/GNU/gawk
  "482b6a1dc55a012c6f4366e3c98971d59bb3a8d5": "2019-05-11T10:05:28.959Z", # RiscOS/Tools/Sources/GNU/gnudiff
  "13d9a0d672689ed885f1483040d8b93052f5dccf": "2019-05-11T10:11:29.869Z", # RiscOS/Tools/Sources/GNU/grep
  "c2945bb2d96d6c606153e815fca6940d8dfdd779": "2019-05-11T10:11:37.065Z", # RiscOS/Tools/Sources/GNU/ident
  "d6d4c8a780a45acbbfbf737ffd95ccc580f3c1ae": "2019-05-11T10:12:38.691Z", # RiscOS/Sources/Lib/ImageLib
  "e6547e2615d582f148599b583a5d4b99e242d7ff": "2019-05-11T10:13:05.469Z", # RiscOS/Sources/Video/HWSupport/IMXVideo
  "0004e1f85f38461924728a42d70b5e9eb23213b7": "2019-05-11T10:15:20.288Z", # RiscOS/Sources/Video/Render/JCompMod
  "73fb7629d2f9fd621b83156d2cf2551d355df77f": "2019-05-11T10:15:33.560Z", # RiscOS/Tools/Sources/GNU/libgnu4
  "44bb8972b4e70e8ffae79094d69b4235f2981c84": "2019-05-11T10:15:49.127Z", # RiscOS/Tools/Sources/GNU/libgnu
  "e5f8f7b49c51cf599b2a077d21e68935b17fa389": "2019-05-11T10:16:38.824Z", # RiscOS/Sources/Lib/mbedTLS
  "b18e105a06dbfa32914ec327a885a774bc925560": "2019-05-11T10:17:03.613Z", # RiscOS/Sources/HWSupport/USB/Controllers/OHCIDriver
  "daf518f90dea7c24ad858b0f74b390be6836c9db": "2019-05-11T10:17:27.832Z", # RiscOS/Sources/Lib/OSLib
  "55eb4abc55cde0e4c58d3447f3e1db09303f4d36": "2019-05-11T10:17:57.534Z", # RiscOS/Utilities/Perl
  "9a8aee3cdb9c5dd4a3f5ae7dc2700380397e3dfe": "2019-05-11T10:18:06.785Z", # RiscOS/Tools/Sources/GNU/readelf
  "d1465d72bb7ea93d93e1f4fd516c50a41d24cf2a": "2019-05-11T10:18:15.348Z", # RiscOS/Sources/Networking/AUN/RouteD
  "319fea697572f34e7d8c70c7af0c22fd2cfe4fbb": "2019-05-11T10:18:38.220Z", # RiscOS/Tools/Sources/GNU/sed
  "84ad545c8c98ad847bcafa8ae8a7a66632fd285e": "2019-05-11T10:19:22.804Z", # RiscOS/Sources/Video/Render/SprExtend
  "fedfb7075eca59d2c873f258d90092988f035dc0": "2019-05-11T10:29:58.620Z", # RiscOS/Sources/HWSupport/VCHIQ
  "fc843a66ef4651b6d5eb3d0361dc7ffdbae5aab8": "2019-05-11T10:30:10.502Z", # RiscOS/Sources/HWSupport/VFPSupport
  "296bfe0862e29b15d936d2408768f1f4fdb7814f": "2019-05-11T10:30:36.111Z", # RiscOS/Sources/Lib/zlib
  "e06361066c74f0ad10d84d6f40cdd9c1aadbac7f": "2019-05-11T13:59:51.247Z", # Products/All
  "9b15a8d7217faaab83202987d714118a24e21f3a": "2019-05-11T14:00:04.065Z", # Products/Batch1to6
  "77e6ff5ec215906cfad66c994cdc57df2774f9d6": "2019-05-11T14:00:10.832Z", # Products/BCM2835
  "46bcff2948819bd199ab830ef680d183d24703d2": "2019-05-11T14:00:18.101Z", # Products/BCM2835Pico
  "1ffd242594342117e45b0357d6b4086e45b64514": "2019-05-11T14:00:24.103Z", # Products/BonusBin
  "ad179f963a9250e4626fd68f2377a88398443e7b": "2019-05-11T14:00:29.204Z", # Products/BuildHost
  "dbe40f6e7f9426678e25b8f2e421f4ad35637fcf": "2019-05-11T14:00:42.891Z", # Products/Disc
  "11347cf5c2cd20d605c75c01f2c2d2d399e7d049": "2019-05-11T14:00:49.802Z", # Products/iMx6
  "95f44d09a7680963b0d0a7ec3e1151d60cab0ed0": "2019-05-11T14:00:55.393Z", # Products/IOMDHAL
  "050926a51786d4aedf2c993c03eae44846ad6655": "2019-05-11T14:01:02.892Z", # Products/OMAP3
  "d71cc6a7b377ca203bf4a2b63e5876cee0ab3d96": "2019-05-11T14:01:10.559Z", # Products/OMAP4
  "ace3d0acdbde1b7412d28f6c184e9df8ed6fcb72": "2019-05-11T14:01:16.697Z", # Products/OMAP5
  "b08c52798452894c648f32d3852b1d6a112a222f": "2019-05-11T14:01:21.801Z", # Products/PlingSystem
  "df5b7fa8992c3041c3d6513b6d8290b2c1491e57": "2019-05-11T14:01:26.788Z", # Products/S3C
  "9995499ef13e4886281d69da7b658aa0f5cc0792": "2019-05-11T14:01:32.304Z", # Products/Titanium
  "829275201b89da333632998b21c243eb50e52e02": "2019-05-11T14:01:39.816Z", # Products/Tungsten
  "ee6a4a83c4ad32bf0fa52c324f65fcadb3b3d922": "2019-05-14T16:40:27.473Z", # Products/Titanium
  "73534cde8cc60fc1b896f968d31a4f09d0166e40": "2019-05-23T05:17:25.152Z", # RiscOS/Sources/SystemRes/InetRes
  "2335669ef0fd2330a2a9f02c807917d0d4de4f6e": "2019-05-23T11:41:40.732Z", # RiscOS/Library
  "16d75e8bed69636d571d1652a135b439c006dc1e": "2019-05-23T14:08:43.134Z", # RiscOS/BuildSys
  "e66f346e23654c15154efef6c8152bc3cc9bf521": "2019-05-24T07:07:49.948Z", # RiscOS/Apps/PlingPrepare
  "64414d7910135ee5ca20f086ca2cdeace59d5afa": "2019-05-24T18:05:36.882Z", # RiscOS/BuildSys
  "348ee0e441ad46861b5785607df81af8914cc868": "2019-05-25T07:59:53.216Z", # Products/All
  "003f6b2bc48f9f712890833592de890a31185e0c": "2019-06-01T14:00:50.123Z", # RiscOS/Sources/Apps/Maestro
  "873c210685052b04d1bf304b7753c9c6ce9712ec": "2019-06-03T13:22:41.618Z", # RiscOS/Sources/Networking/Omni/Protocols/OmniLanManFS
  "09cc90aee795743414b9d83b9f987a68fa5f20f8": "2019-06-04T22:01:18.357Z", # RiscOS/Env
  "5ad5163bdd1f6ce10f9ca440b8291e9f951a620a": "2019-06-04T22:01:46.641Z", # RiscOS/Sources/Networking/Omni/Protocols/OmniLanManFS
  "39485b7c7a80fa91ed41410703b67b9b4fd734c4": "2019-06-05T20:19:19.552Z", # RiscOS/Sources/Desktop/Wimp
  "c2f5455f14e4607202d61ecfc01d5822bfa6274b": "2019-06-08T07:59:05.291Z", # RiscOS/Sources/Desktop/TaskWindow
  "fbb7e4e073f9ca02980f5f1bbe01b58443112c2f": "2019-06-08T10:37:33.780Z", # RiscOS/Sources/Apps/Paint
  "0857587f531ef24b428edbd68ae34c66338993eb": "2019-06-08T10:46:24.052Z", # RiscOS/Sources/Apps/Draw
  "6982f5cceafbb64e359693ba75d8c58ad8e1b6ff": "2019-06-09T21:22:32.257Z", # RiscOS/Sources/Lib/RISC_OSLib
  "0289650a6f5c432246593d8ddbd402cd6aa9dbe6": "2019-06-18T12:48:44.597Z", # RiscOS/Sources/FileSys/PCCardFS/PCCardFS
  "7c2fe7dcb78bcd128b48af582788e24c8737d5d0": "2019-06-18T15:43:40.086Z", # RiscOS/Sources/HAL/HAL_BCM2835
  "e1160d90d0e994a51890e60d8eec2e7818adb2bb": "2019-06-22T11:41:38.591Z", # RiscOS/Sources/Lib/mbedTLS
  "87ea8ac2cf8798fab1a3ff020d5299c3f083c94b": "2019-06-22T16:51:04.333Z", # RiscOS/Sources/Desktop/Wimp
  "ad29219032d67959617dc8470dc83cbf08c3b4fa": "2019-06-24T21:45:18.564Z", # RiscOS/Sources/Programmer/HdrSrc
  "e604b89ce92dad772a442c1fb9f72d60b11aba3e": "2019-06-24T21:46:31.591Z", # RiscOS/Sources/Kernel
  "360be29044c7fe9d2f3f1f74b996bb2dee1af963": "2019-06-24T21:47:40.173Z", # RiscOS/Sources/Video/HWSupport/BCMVideo
  "620ec992c0a72a5b7983f6efd1bf4b0da380bb0d": "2019-06-28T12:59:29.331Z", # RiscOS/Sources/FileSys/FSLock
  "ff78d99712621f87e861df9f4e06fe65efcf311f": "2019-06-29T07:45:38.988Z", # RiscOS/Sources/HWSupport/SD/SDIODriver
  "d71c49f81711759c10c6b25484cb8175949a38df": "2019-06-29T07:45:51.241Z", # RiscOS/Sources/HWSupport/BCMSupport
  "a85663de64ae3097612dd28ed3de67480331dc7c": "2019-06-29T07:46:20.460Z", # RiscOS/Sources/Programmer/BASIC
  "fc49beafd833cc4dde7cfc2af1b1e1d2e217ac6a": "2019-07-02T22:04:06.248Z", # RiscOS/Sources/Kernel
  "b613fdbbb57aa944090a107e6dbfaf7e6158b6ef": "2019-07-02T22:04:32.374Z", # RiscOS/Sources/Video/UserI/ScrModes
  "f5de9f4a23052a92f0e3028d21da0ccc79073c7d": "2019-07-02T22:05:06.444Z", # RiscOS/Sources/Video/HWSupport/BCMVideo
  "5822bffa06945f812a55af5c63f05bc93e64efef": "2019-07-02T22:05:55.239Z", # RiscOS/Sources/Video/HWSupport/GC320VideoBlob
  "ada0df77886b1845164f9806a29b02cc2c5d15d4": "2019-07-02T22:06:15.322Z", # RiscOS/Sources/Video/HWSupport/IMXVideo
  "f4ee826b179316478c331f54ffe7e3b41cab78c7": "2019-07-02T22:06:28.093Z", # RiscOS/Sources/Video/HWSupport/NVidia
  "e285399de40410e733031424db5ecdd6309dd1f9": "2019-07-02T22:06:41.337Z", # RiscOS/Sources/Video/HWSupport/OMAPVideo
  "26c7a3f93253daf6fdd6283e7b0cd07889c5cd6b": "2019-07-02T22:07:18.008Z", # RiscOS/Sources/Video/HWSupport/VIDC20Video
  "eefda4a2662e4746944a5fceb58fa114a4f9387b": "2019-07-02T22:11:51.702Z", # RiscOS/Sources/Video/HWSupport/UDLVideo
  "9a09a85589cd1a79315e77d1b363af901a322115": "2019-07-06T08:34:21.460Z", # RiscOS/Sources/Programmer/Debugger
  "742c9bef8ae0230874d6699a96f57b3d5af36053": "2019-07-06T08:34:34.479Z", # RiscOS/Library
  "e19eb2738bdc38b77ecef9d45e49975084a929bd": "2019-07-06T08:35:11.430Z", # RiscOS/Sources/Video/HWSupport/BCMVideo
  "1f78441a44e6354557d9d2d0b40f60bd9cf4ef6d": "2019-07-06T08:35:23.822Z", # RiscOS/Sources/Video/HWSupport/OMAPVideo
  "20984a33bfc81596f3cced8be169f4d3c213a58d": "2019-07-08T22:50:22.288Z", # RiscOS/Sources/Lib/RISC_OSLib
  "0e991b6b4842d25df785dd685c808b5ca631e550": "2019-07-13T07:35:56.723Z", # RiscOS/Sources/Lib/NBLib
  "ef64e1a4070a41a24da5c40181df56d3a4f4806c": "2019-07-15T20:10:51.941Z", # RiscOS/Sources/Video/HWSupport/OMAPHDMIBlob
  "79a725757b2987e1f01a40f57b6ff65a47cc44a9": "2019-07-15T20:11:09.829Z", # RiscOS/Sources/Programmer/HdrSrc
  "f8dae0561762272380044f8aebf83783a7978e72": "2019-07-20T07:12:16.811Z", # RiscOS/Sources/HWSupport/BCMSupport
  "903f38920bf6c5d3942ac9e6d195a544477e0b18": "2019-07-20T07:13:05.553Z", # RiscOS/Sources/HWSupport/SD/SDIODriver
  "7cebc1640b36ab9f44ec483c13a442f7d58b4b9c": "2019-07-20T07:18:56.685Z", # RiscOS/Sources/HAL/HAL_OMAP5
  "4022e43f3e11dd3f22498ec48d8a021923aeb20d": "2019-07-20T07:39:50.615Z", # RiscOS/BuildSys
  "37d148dd60fd7d1dca4a99bac13d7348e1230b3a": "2019-07-20T08:21:46.545Z", # Products/OMAP5
  "14d0a6d62bbbe7f5a12c510a9a9e4c2f6f1ab38d": "2019-07-27T08:07:19.378Z", # RiscOS/Sources/Lib/RISC_OSLib
  "12a389b23a27a00ec36d2b23b0e62034ea2a63d0": "2019-08-03T21:20:14.347Z"  # RiscOS/Sources/HAL/HAL_BCM2835
}

rearrange_date = datetime.datetime(2011, 3, 17, 19, 32).timestamp()
cvs_end_date = datetime.datetime(2019, 5, 1).timestamp()

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

def load_repository(name, repo, prefix="refs/heads/"):

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

    commits = dict()
    refs = dict()

    for ref1 in repo.listall_references():
        if ref1.startswith(prefix):
            ref = repo.lookup_reference(ref1)
            if ref.type == pygit2.GIT_REF_OID:
                ref1 = ref1[len(prefix):]
                commit_list = list(load_commit(ref.target))
                min_time = 0
                for commit in reversed(commit_list):
                    if commit.committer.time < min_time:
                        commit.committer = pygit2.Signature(email=commit.committer.email, name=commit.committer.name, time=min_time)
                    new_time = redate_map.get(str(commit.oid))
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
