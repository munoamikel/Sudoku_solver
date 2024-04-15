#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 11:15:00 2023

@author: juanmi
"""


import argparse
from typing import Tuple

from pysat.formula import CNF
from pysat.solvers import Solver , Glucose3


import math

import string

import os

import pickle
import json

import time
import re

def err(mezua):
    print(mezua)
    exit(1)

def var_inv(literal):
    value = (literal-1) % N + 1
    column = ((literal-1) // N) % N + 1
    row = ((literal-1) // N) // N + 1
    return (row, column, value)

def var(row, column, value):
    return (row-1)*N*N + (column-1)*N + value

def display_solution(model, number, all_solutions):
    
    
    solution = {}
    for literal in model:
        if 0 < literal <= N*N*N:
            # The positive encoding literals give us the values
            (row, column, value) = var_inv(literal)
            if (row, column) in solution:
                err(f'Found a solution with two values '
                    f'for the cell at ({row}, {column})')
            solution[(row, column)] = value
    validate_solution(solution, clues)
    
    if all_solutions == False:
        size = "9x9/" if "9x9" in clues else "25x25/"         
        
    else:
        size = "all9x9/" if "all9x9" in clues else "all25x25/" 
        
    # # Display the solution
    # for row in range(1, N+1):
    #     print(' '+' '.join([str(solution[(row, column)])
    #                         for column in range(1, N+1)]))
    # print('')
    
    # #SAVE OUTPUT TO A FILE (PARAMETERIZE IT ACCORDING TO THE DIMENSIONS)
    # size = "9x9/" if "9x9" in clues else "25x25/" 
    
    with open('./outputs/' + size + os.path.basename(clues), 'w+') as f:                
        for row in range(1, N+1):
            f.write(' '+' '.join([str(solution[(row, column)])
                                for column in range(1, N+1)]))
            f.write('\n')
    
    with open('./outputs/' + size + os.path.basename(clues) + '_' + str(number) + '.html' ,'w+') as f2: 
        
        grid = open('./outputs/' + size + os.path.basename(clues)).read()
        
        first = str(D)+'n'
        second = 'n+'+str(N)
        
        html = '''
            <html>
            <head>
            <style>
            table {
              border-collapse: collapse;
            }
            
            td {
              border: 1px solid black;
              width: 30px;
              height: 30px;
              text-align: center;
            }
            
            tr:nth-child(
            '''
        html+= first 
        html+= '''
            ) td {
              border-bottom: 10px solid black; 
            }
            
            tr:nth-child(
            '''
        html+= second
        html+= '''
            ) td {
              border-bottom: 1px solid black;
            } 
            
            td:nth-child(
            '''
        html+= first 
        html+= '''
            ) {
              border-right: 10px solid black;
            }
            
            td:nth-child(
            '''
        html+= second 
        html+= '''
            ) {
              border-right: 1px solid black; 
            }
            </style>
            </head>
            <body>
            '''
            
        html += '<table>'

        for line in grid.split('\n'):
          html += '<tr>'

          for num in line.split():
            html += f'<td>{num}</td>'

          html += '</tr>'

        html += '</table>'
        
        html += '''
            </body>
            </html>
            '''
        
        f2.write(html)
        

def encode(clues):
    
    cnf = CNF()

    
    
    return cnf

       


#Lerro bakoitzeko dagozkion N elementuak daude    
def row_clauses(clauses,N):
    for row in range(1, N+1):
        for value in range(1, N+1):
            clause = []
            for column in range(1, N+1):
                clause.append(var(row, column, value))
            clauses.append(clause)
    return clauses

#Zutabe bakoitzeko dagozkion N elementuak daude
def column_clauses(clauses,N):
    for column in range(1, N+1):
        for value in range(1, N+1):
            clause = []
            for row in range(1, N+1):
                clause.append(var(row, column, value))
            clauses.append(clause)
    return clauses

#Karratu bakoitzeko dagozkion N elementuak daude
def square_clauses(clauses,N):
    for row in range(1, D+1):
        for column in range(1, D+1):
            for value in range(1, N+1):
                clause = []
                for i in range(1, D+1):
                    for j in range(1, D+1):
                        clause.append(var((row-1)*D+i, (column-1)*D+j, value))
                clauses.append(clause)
    return clauses

#Ziurtatu matrizearen posizio bakoitzeko elementu bakarra dagoela
def one_value_clauses(clauses,N):
    for row in range(1, N+1):
        for column in range(1, N+1):
            for value1 in range(1, N):
                for value2 in range(value1+1, N+1):
                    clauses.append([-var(row, column, value1), -var(row, column, value2)])
    return clauses

def pre_encode(dim):
    clauses = []
    row_clauses(clauses,dim)
    column_clauses(clauses,dim)
    square_clauses(clauses,dim)
    one_value_clauses(clauses,dim)
    cnf = CNF()
    cnf.extend(clauses)
    return cnf

def encode(clues):
    assumptions = []
    f = open(clues)
    pista = json.load(f)
    for row in range(len(pista)):
        for column in range(len(pista)):
            if pista[row][column] != NOCLUE:
                pista[row][column] = str(pista[row][column])

                #OPTIMIZAZIOA

                if N == 9:
                    #append clues(Rule1: literal bakarreko klausulaen literalak egiazkoak dira)
                    assumptions.append(var(row+1, column+1, DIGITS[pista[row][column]]))

                    #append negated clues
                    #Jakinda aldagai bakoitzeko bakarrik 1 balio posible dago, beste balio bat ezin da egon
                    for value in range(1, N+1):
                        if value != DIGITS[pista[row][column]]:
                            assumptions.append(-var(row+1, column+1, value))
                    
                    for other_row in range(1, N+1):
                        if other_row != row+1:
                            assumptions.append(-var(other_row, column+1, DIGITS[pista[row][column]]))
                    for other_column in range(1, N+1):
                        if other_column != column+1:
                            assumptions.append(-var(row+1, other_column, DIGITS[pista[row][column]]))
                    i = int((row)/D)
                    j = int((column)/D)
                    for other_row in range(1, D+1):
                        for other_column in range(1, D+1):
                            if other_row + i*D != row+1 and other_column + j*D != column+1:
                                assumptions.append(-var((i*D)+other_row, (j*D)+other_column, DIGITS[pista[row][column]]))
                else:
                    assumptions.append(var(row+1, column+1, letter_to_num[pista[row][column]]))
                    for value in range(1, N+1):
                        if value != letter_to_num[pista[row][column]]:
                            assumptions.append(-var(row+1, column+1, value))
                    for other_row in range(1, N+1):
                        if other_row != row+1:
                            assumptions.append(-var(other_row, column+1, letter_to_num[pista[row][column]]))
                    for other_column in range(1, N+1):
                        if other_column != column+1:
                            assumptions.append(-var(row+1, other_column, letter_to_num[pista[row][column]]))
                    i = int((row)/D)
                    j = int((column)/D)
                    for other_row in range(1, D+1):
                        for other_column in range(1, D+1):
                            if other_row + i*D != row+1 and other_column + j*D != column+1:
                                assumptions.append(-var((i*D)+other_row, (j*D)+other_column, letter_to_num[pista[row][column]]))
    return assumptions



def solve_and_decode(assumptions, cnf, all_solutions):
    solver = Glucose3()
    solver.append_formula(cnf)
    if all_solutions:
        iter = 0
        while solver.solve(assumptions= assumptions):
            model = solver.get_model()
            display_solution(model, iter, all_solutions)
            solver.add_clause([-literal for literal in model])
            iter += 1
        print("No more solutions found!")
    else:
        if solver.solve(assumptions= assumptions):
            model = solver.get_model()
            display_solution(model, 1, all_solutions)
        else:
            print("No solution found!")


def validate_solution(solution, clues):
    for row in range(1, N+1):
        for column in range(1, N+1):
            if (row, column) not in solution:
                err(str((row,column) , "gelaxka hutsa dago"))
            if solution[(row, column)] not in range(1, N+1):
                err(str(row,column),"zenbakia ez dago dimentsioaren barruan")
    for row in range(1, N+1):
        for column in range(1, N+1):
            value = solution[(row, column)]
            for other_column in range(1, N+1):
                if other_column != column and solution[(row, other_column)] == value:
                    err("2 aldiz agertzen da zenbakia")
            for other_row in range(1, N+1):
                if other_row != row and solution[(other_row, column)] == value:
                    err("2 aldiz agertzen da zenbakia")
    for row in range(1, D+1):
        for column in range(1, D+1):
            values = set()
            for i in range(1, D+1):
                for j in range(1, D+1):
                    values.add(solution[((row-1)*D+i, (column-1)*D+j)])
            if len(values) != N:
                err("2 aldiz agertzen da zenbakia)")
    
    

def solve_sudoku(clues,pre_cnf ,all_solutions):
    ass = encode(clues)
    solve_and_decode(ass, pre_cnf, all_solutions)
    #print("Done!")

if __name__ == '__main__':
    time_start = time.time()
    files_9x9 = [os.path.join('./inputs/9x9/', f) for f in os.listdir('./inputs/9x9/') if f.endswith('.json')]
    files_25x25 = [os.path.join('./inputs/25x25/', f) for f in os.listdir('./inputs/25x25/') if f.endswith('.json')]
    
    files_all9x9 = [os.path.join('./inputs/all9x9/', f) for f in os.listdir('./inputs/all9x9/') if f.endswith('.json')]
    
    # Create directories
    dirs = [
        './outputs',
        './outputs/9x9',
        './outputs/all9x9',
        './outputs/25x25',
        './outputs/all25x25'
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            
    # The symbols allowed in the Sudoku instance text file
    # DIGITS from 1 to 9 in 9x9, A to Y -> 1 to 25 in 25x25
    DIGITS = {}
    for i in range(1, 9+1):
        DIGITS[str(i)] = i
          
    NOCLUE = '.'
    
    letters = string.ascii_uppercase[:25]
    digits = range(1, 25+1)
    letter_to_num = {}
    for letter, digit in zip(letters, digits):
        letter_to_num[letter] = digit

    D = 3 
    N=9
    cnf = pre_encode(N)
    for clues in files_9x9:
        with open(clues, "rb") as f:
            lines = json.load(f)
            
            is_square = int(3 + 0.5) ** 2 == len(lines)
            if not is_square:
                print("input incorrect!!!")
                exit(0)
    
            D = int(math.sqrt(len(lines))) 
            N = D*D 
        
            DIGITS = {}
            for i in range(1, N+1):
                DIGITS[str(i)] = i
                  
            NOCLUE = '.'
            
            solve_sudoku(clues,cnf,False)
    print("9x9 solved!")
    print("Total time: " + str(time.time() - time_start) + " seconds")

    print("Starting all9x9...")
    D = 3 
    N=9
    cnf = pre_encode(N)
    for clues in files_all9x9:
        with open(clues, "rb") as f:
            lines = json.load(f)
            
            is_square = int(3 + 0.5) ** 2 == len(lines)
            if not is_square:
                print("input incorrect!!!")
                exit(0)
    
            D = int(math.sqrt(len(lines)))
            N = D*D
        
            solve_sudoku(clues,cnf,True)
    print("all9x9 solved!")
    
    
    D=5
    N=25
    cnf = pre_encode(N)
    for clues in files_25x25:
        
        with open(clues, "rb") as f:
            time_start = time.time()
            lines = json.load(f)
            
            is_square = int(5 + 0.5) ** 2 == len(lines)
            if not is_square:
                print("input incorrect!!!")
                exit(0)
                
            D = int(math.sqrt(len(lines))) 
            N = D*D 
            
            print("Solving: " + clues)
            solve_sudoku(clues, cnf,False)
            print(clues + " solved!")