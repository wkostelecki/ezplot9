SYMBOLS_TO_IGNORE = ['==', '>=', '<=', '!=', '+=', '-=', '*=', '/=', '**=', '%=', '//=']
OPERATORS_TO_REPLACEMENT_KEYS={s:s.replace('=', '~~') for s in SYMBOLS_TO_IGNORE}

def unname(x):
    '''
    Simple function for parsing input variable strings. The function extracts the name for labelling and the
    expression to be evaluated

    Parameters
    ----------
    x : str
        string representing a variable

    Returns
    -------
    name :  str
        variable name
    var : str
        variable expression

    '''

    if x is None:
        var=None
        name=None

    elif isinstance(x, str):

        # check if there is a name to be extracted
        if '=' in x:

            # check if the equal sign was used in an operator
            operators_present = [s for s in SYMBOLS_TO_IGNORE if s in x]
            if len(operators_present)==0:
                # separate name and expression
                var = x.split('=', 1)[1]
                name = x.split('=', 1)[0].replace(' ', '')

            else:
                # replace operators with keys and extract name and var
                x_mod = x
                for op in operators_present:
                    x_mod = x_mod.replace(op, OPERATORS_TO_REPLACEMENT_KEYS[op])

                name, mod_var = unname(x_mod)

                var = mod_var
                for op in operators_present:
                    var = var.replace(OPERATORS_TO_REPLACEMENT_KEYS[op], op)

                if mod_var == name:
                    name=var.replace(' ', '')

        else:
            var=x
            name=x.replace(' ', '')

    return name, var