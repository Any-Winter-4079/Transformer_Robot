import re
import string
import numpy as np
from sympy import solve, sympify, Symbol
from config.v3.config import MODEL_TEMPLATE, STOP
from utils.v3.utils import run_llm, extract_and_format_value
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

# (start of) Declarative -> https://github.com/joyheyueya/declarative-math-word-problem.git (adapted)
def simplify_variables(equations):
    var_names = set(re.findall(r'\b[a-zA-Z_]\w*\b', equations))
    long_var_names = [var for var in var_names if len(var) > 1]
    unused_chars = [chr(i) for i in range(97, 123) if chr(i) not in var_names]  # a-z
    var_mapping = {var: unused_chars.pop(0) for var in long_var_names}
    
    for long_var, short_var in var_mapping.items():
        equations = re.sub(r'\b{}\b'.format(long_var), short_var, equations) 
    return equations, var_mapping

def clean_equation_text(equation_text):
    cleaned_equation_text = re.sub(r'[^\w\s=+\-*/()0-9.\[\]]', '', equation_text)
    return cleaned_equation_text

def reformat_incre_equations(x):
    result = ''
    if len(x) >= 1:
        for eq in x:
            if len(result) == 0:
                result += eq[2 : -2]
            else:
                result += ', ' + eq[2 : -2]
    return result

def reformat_equations_from_peano(eq_list):
    result = ''
    for eq in eq_list.split(','):
        if 'eq' in eq:
            if len(result) == 0:
                result += eq[eq.index('eq') + 2:]
            else:
                result += ', ' + eq[eq.index('eq') + 2:]
        elif 'answer' in eq:
            if len(result) == 0:
                result += eq[eq.index('answer') + 6:].strip() + ' = ?'
            else:
                result += ', ' + eq[eq.index('answer') + 6:].strip() + ' = ?'     
    return result

def get_declarative_equations(prediction):
    eq_list = re.findall(r'\[\[.*?\]\]', prediction)
    
    cleaned_eq_list = []
    
    if len(eq_list) > 0:
        for eq in eq_list:
            cleaned_eq = clean_equation_text(eq)
            cleaned_eq_list.append(cleaned_eq)
        
        return reformat_equations_from_peano(reformat_incre_equations(cleaned_eq_list))
    else:
        return prediction

def get_final_using_sympy(equations):
    try:
        equations, _ = simplify_variables(equations)
        transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
        if str(equations) == 'nan':
            return np.nan
        equation_list = equations.split(',')
        for eq in equation_list:
            for c in range(len(eq)):
                if c < len(eq) - 2:
                    if eq[c].isalpha() and eq[c+1].isalpha() and eq[c+2].isalpha():
                        return 'invalid equations'

        goal_var = None
        goal_expression_list = []
            
        if equation_list[-1].split('=')[0].strip().isalpha() or len(equation_list[-1].split('=')[0].strip()) == 2:
            goal_var = equation_list[-1].split('=')[0].strip()
        elif '=' in equation_list[-1]:
            for l in list(string.ascii_lowercase) + list(string.ascii_uppercase):
                if l not in equation_list[-1]:
                    goal_var = l
                    break
            if goal_var is not None:
                goal_expression = goal_var + ' - (' + equation_list[-1].split('=')[0].strip() + ')'
                goal_expression = parse_expr(goal_expression, transformations=transformations)
                goal_expression = sympify(goal_expression)
                try:
                    return float(solve(goal_expression)[0])
                except Exception as e:
                    pass
                goal_expression_list.append(goal_expression)
            else:
                return 'invalid equations'

        if len(equation_list) == 1:
            try:
                goal_expression = parse_expr(equation_list[0].split('=')[0], transformations=transformations)
                return float(sympify(goal_expression))
            except Exception as e:
                return 'invalid equations'

        if goal_var == None:
            return 'no goal found'

        for i in range(len(equation_list) - 1):
            sub_eqs = equation_list[i]  
            if '?' not in sub_eqs:
                try:    
                    sub_eqs_split = sub_eqs.split('=')
                    sub_eqs = sub_eqs_split[0].strip() + ' - (' + sub_eqs_split[1].strip() + ')'
                    sub_eqs = parse_expr(sub_eqs, transformations=transformations)
                    sub_eqs = sympify(sub_eqs)
                except Exception as e:
                    return 'invalid equations'
                goal_expression_list.append(sub_eqs)

                try:
                    try:
                        return float(solve(goal_expression_list)[Symbol(goal_var)])
                    except Exception as e:
                        return float(solve(goal_expression_list)[0][Symbol(goal_var)])
                except Exception as e:
                    pass

        return 'no solution'
    except Exception as e:
        print(e)
        return 'bug'
# (end of) Declarative -> https://github.com/joyheyueya/declarative-math-word-problem.git (adapted)

# Function to run the Declarative method
def run_declarative(question, exemplars, cpp=False, iteration=0):
    """Run the Declarative method."""
    user_end = MODEL_TEMPLATE["user_end"]
    assistant_start = MODEL_TEMPLATE["assistant_start"]
    message = f"{exemplars}{question}{user_end}\n{assistant_start}"
    prediction = run_llm(message, STOP, cpp=cpp, iteration=iteration)
    eq_list = get_declarative_equations(prediction)
    # print(f"\tDecl: {eq_list}")
    concise_prediction = get_final_using_sympy(eq_list)
    if concise_prediction in ["invalid equations", "no goal found", "no solution", "bug"]:
        concise_prediction = "bug"
    else:
        concise_prediction = extract_and_format_value(concise_prediction)
    print("\tDecl:", concise_prediction)
    prediction = f"{prediction}\n#### {concise_prediction}"
    return message, prediction, concise_prediction
