#!/usr/bin/env python3
"""
601.465/665 — Natural Language Processing
Assignment 1: Designing Context-Free Grammars

Assignment written by Jason Eisner
Modified by Kevin Duh
Re-modified by Alexandra DeLucia

Code template written by Alexandra DeLucia,
based on the submitted assignment with Keith Harrigian
and Carlos Aguirre Fall 2019
"""
import argparse
import os
import random
import subprocess
import sys
import copy

# Want to know what command-line arguments a program allows?
# Commonly you can ask by passing it the --help option, like this:
#     python randsent.py --help
# This is possible for any program that processes its command-line
# arguments using the argparse module, as we do below.
#
# NOTE: When you use the Python argparse module, parse_args() is the
# traditional name for the function that you create to analyze the
# command line.  Parsing the command line is different from parsing a
# natural-language sentence.  It's easier.  But in both cases,
# "parsing" a string means identifying the elements of the string and
# the roles they play.

def parse_args():
    """
    Parse command-line arguments.

    Returns:
        args (an argparse.Namespace): Stores command-line attributes
    """
    # Initialize parser
    parser = argparse.ArgumentParser(description="Generate random sentences from a PCFG")
    # Grammar file (required argument)
    parser.add_argument(
        "-g",
        "--grammar",
        type=str, required=True,
        help="Path to grammar file",
    )
    # Start symbol of the grammar
    parser.add_argument(
        "-s",
        "--start_symbol",
        type=str,
        help="Start symbol of the grammar (default is ROOT)",
        default="ROOT",
    )
    # Number of sentences
    parser.add_argument(
        "-n",
        "--num_sentences",
        type=int,
        help="Number of sentences to generate (default is 1)",
        default=1,
    )
    # Max number of nonterminals to expand when generating a sentence
    parser.add_argument(
        "-M",
        "--max_expansions",
        type=int,
        help="Max number of nonterminals to expand when generating a sentence",
        default=450,
    )
    # Print the derivation tree for each generated sentence
    parser.add_argument(
        "-t",
        "--tree",
        action="store_true",
        help="Print the derivation tree for each generated sentence",
        default=False,
    )
    return parser.parse_args()


class Grammar:
    def __init__(self, grammar_file):
        """
        Context-Free Grammar (CFG) Sentence Generator

        Args:
            grammar_file (str): Path to a .gr grammar file
        
        Returns:
            self
        """
        # Parse the input grammar file
        self.rules = None
        self._load_rules_from_file(grammar_file)

    def _load_rules_from_file(self, grammar_file):
        """
        Read grammar file and store its rules in self.rules

        Args:
            grammar_file (str): Path to the raw grammar file 
        """
        rules = {}
        
        with open(grammar_file) as grammar:
            content = grammar.read().splitlines()
            for line in content:
                if not line or line.startswith('#'):
                    continue
                line = line.split('#')[0].strip()
                
                # segment each line into three parts
                segments = line.split('\t')
                # print(segments)
                segments[2] = segments[2].split(' ')
                # print(segments)
                
                # create a probability-dependent dictionary
                if segments[1] not in rules:
                    rules[segments[1]] = []
                rules[segments[1]].append((float(segments[0]), segments[2]))
                
        # print(rules)
        self.rules = rules
        
    def dfs_expansion(self, string_segments, max_expansions_pass, derivation_tree):
        # print(string_segments)
        for index, segments in enumerate(string_segments):
            if max_expansions_pass[0] <= 0:
                string_segments[index] = '...'
                return string_segments, max_expansions_pass
            if isinstance(segments, list):
                # print('segments', segments)
                # print('string_segments[index]', string_segments[index])
                self.dfs_expansion(string_segments[index], max_expansions_pass, derivation_tree)
            elif segments in self.rules:
                # print('not list')
                temp_rules = self.rules[segments]
                weight = []
                for temp_rule in temp_rules:
                    weight.append(temp_rule[0])
                if not derivation_tree:
                    string_segments[index] = copy.deepcopy(random.choices(temp_rules, weights=weight, k=1)[0][1]) # a list, in the form ['S', '.']
                else:
                    string_segments[index] = [(string_segments[index],), copy.deepcopy(random.choices(temp_rules, weights=weight, k=1)[0][1])]
                max_expansions_pass[0] = max_expansions_pass[0] - 1
                self.dfs_expansion(string_segments[index], max_expansions_pass, derivation_tree)
            else: # terminus
                pass
                
        return string_segments, max_expansions_pass
        
    
    def dfs_print(self, string_segments, print_form):
        for index, segments in enumerate(string_segments):
            if isinstance(segments, list):
                self.dfs_print(segments, print_form)
            else:
                print_form.append(segments)
        return print_form
    
    def dfs_print_tree(self, string_segments, sentence):
        for index, segments in enumerate(string_segments):
            # print(segments)
            if isinstance(segments, list):
                sentence.append('(')
                self.dfs_print_tree(string_segments[index], sentence)
                sentence.append(')')
            elif isinstance(segments, tuple):
                sentence.append(segments[0])
            else:
                sentence.append(segments)
        return sentence

    def sample(self, derivation_tree, max_expansions, start_symbol):
        """
        Sample a random sentence from this grammar
        Args:
            derivation_tree (bool): if true, the returned string will represent 
                the tree (using bracket notation) that records how the sentence 
                was derived
                               
            max_expansions (int): max number of nonterminal expansions we allow

            start_symbol (str): start symbol to generate from

        Returns:
            str: the random sentence or its derivation tree
        """
        
        max_expansions_pass = [max_expansions]
        string_segments = start_symbol.split(' ') # key variable
        
        string_segments, max_expansions_pass = self.dfs_expansion(string_segments, max_expansions_pass, derivation_tree)
        # the procedure above will produce new_segments = [['NP','VP'], ['.']] etc.
        # print(string_segments)
        
        if not derivation_tree:
            # remove the brackets
            print_form = []
            print_form = self.dfs_print(string_segments, print_form)
            sentence = " ".join(print_form)
        else:
            sentence = []
            sentence = " ".join(self.dfs_print_tree(string_segments, sentence))
            # bracket form
        
        return sentence


####################
### Main Program
####################
def main():
    # Parse command-line options 
    args = parse_args()

    # Initialize Grammar object
    grammar = Grammar(args.grammar)

    # Generate sentences
    for i in range(args.num_sentences):
        # Use Grammar object to generate sentence
        sentence = grammar.sample(
            derivation_tree=args.tree,
            max_expansions=args.max_expansions,
            start_symbol=args.start_symbol
        )

        # Print the sentence with the specified format.
        # If it's a tree, we'll pipe the output through the prettyprint script.
        if args.tree:
            prettyprint_path = os.path.join(os.getcwd(), 'prettyprint')
            subprocess.run(
                ['perl', prettyprint_path],
                input=sentence,
                text=True
            )
        else:
            print(sentence)


if __name__ == "__main__":
    main()
