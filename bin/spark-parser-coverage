#!/usr/bin/env python
#  Copyright (c) 2022 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import os
import pickle

import click

from spark_parser.version import __version__


def sort_profile_info(path, max_count=1000):
    profile_info = pickle.load(open(path, "rb"))

    # Classify unused rules. Some are "unused" because the have nullable
    # nonterminals and those show up as a different rule. Sothe rule
    # *is* used just not in the form where a nullable symbol hasn't been
    # nulled.

    # And in some cases this is intentional. Uncompyle6 creates such grammar
    # rules to ensure that positions of certain nonterminals in semantic
    # actions appear in the same place as similar grammar rules

    unused_rules = set()  # just the grammar rules
    used_rules = []  # (count, grammar rule)
    for rule, count in profile_info.items():
        if count == 0:
            unused_rules.add(rule)
        else:
            used_rules.append((count, rule))

    for count, rule in used_rules:
        if rule.find("\\e_") > -1:
            canonic_rule = rule.replace("\\e_", "", 1000)
            if canonic_rule in unused_rules:
                unused_rules.remove(canonic_rule)
                pass
            pass
        pass

    unused_items = [(0, item) for item in sorted(unused_rules)]
    used_items = sorted(used_rules, reverse=False)
    return [item for item in unused_items + used_items if item[0] <= max_count]


DEFAULT_COVERAGE_FILE = os.environ.get(
    "SPARK_PARSER_COVERAGE", "/tmp/spark-grammar.cover"
)
DEFAULT_COUNT = 100


@click.command()
@click.version_option(version=__version__)
@click.option(
    "--max-count",
    type=int,
    default=DEFAULT_COUNT,
    help=(
        f"limit output to rules having no more than this many hits (default {DEFAULT_COUNT})"
    ),
)
@click.argument("path", type=click.Path(), default=DEFAULT_COVERAGE_FILE)
def run(max_count, path: str):
    """Print grammar reduce statistics for a series of spark-parser parses"""
    for count, rule in sort_profile_info(path, max_count):
        print("%d: %s" % (count, rule))
        pass
    return


if __name__ == "__main__":
    run()
