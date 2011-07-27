# vim:set et sts=4 sw=4:
#
# ibus - The Input Bus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

SHIFT_MASK = 1 << 0
LOCK_MASK = 1 << 1
CONTROL_MASK = 1 << 2
ALT_MASK = 1 << 3
MOD1_MASK = 1 << 3
MOD2_MASK = 1 << 4
MOD3_MASK = 1 << 5
MOD4_MASK = 1 << 6
MOD5_MASK = 1 << 7

#
# lotem 2010-12-03
# modified in Weasel to fit the mask into a UINT16
#
HANDLED_MASK = 1 << 8
IGNORED_MASK = 1 << 9
FORWARD_MASK = 1 << 9

SUPER_MASK = 1 << 10
HYPER_MASK = 1 << 11
META_MASK = 1 << 12

RELEASE_MASK = 1 << 14

MODIFIER_MASK = 0x2fff

MODIFIER_NAME_TABLE = (
    ("Shift", SHIFT_MASK),
    ("CapsLock", LOCK_MASK),
    ("Ctrl", CONTROL_MASK),
    ("Alt", MOD1_MASK),
    ("SUPER", SUPER_MASK),
    ("Hyper", HYPER_MASK),
    ("Meta", META_MASK),
    ("Release", RELEASE_MASK),
)
