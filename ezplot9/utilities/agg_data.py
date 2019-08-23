import pandas as pd
from itertools import product

import logging
log = logging.getLogger(__name__)

DELAYED_VARIABLES_KEY='@'

def agg_data(df,
             variables,
             groups,
             aggfun='sum',
             fill_groups=False):

    '''
    Aggregate the variable columns of a dataframe after grouping.

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe to be aggregated
    variables : dict
        variables dictionary (name:expr or name:list(expr))
    groups : dict
        groups dictionary (name:expr)
    aggfun : str of fun
        function to be used for aggregation
    fill_groups : bool
        make sure that all groups have at least one row in the output dataframe

    Returns
    -------
    out_df : pd.DataFrame
        aggregated dataframe

    '''

    # get groups, varibales and delayed variables
    groups, variables, delayed_variables = get_groups(df, variables,groups)

    # evaluation before aggregating (also changes column names)
    for key, val in dict(variables, **groups).items():
        if val is not None:
            expr = '{}=({})'.format(key, val)
            try:
                df.eval(expr, inplace=True, engine = 'numexpr')
            except Exception as e:
                try:
                    df.eval(expr, inplace=True, engine='python')
                except Exception as e:
                    log.error('The type in {} is not be supported and '
                              'the expression cannot be evaluated.'.format(key))
                    raise e

    # aggregate df
    group_cols = list(groups.keys())

    if aggfun is not None:
        df = df.groupby(group_cols) \
            .agg(aggfun) \
            .reset_index()

    # evaluation after aggregation
    for key, val in delayed_variables.items():
        if not (val is None):
            expr = '{}=({})'.format(key, val)
            try:
                df.eval(expr, inplace=True, engine = 'numexpr')
            except Exception as e:
                try:
                    df.eval(expr, inplace=True, engine='python')
                except Exception as e:
                    log.error('The type in {} is not be supported and '
                              'the expression cannot be evaluated.'.format(key))
                    raise e

    # select output
    all_variables = list(set(variables.keys()) | set(delayed_variables.keys()))
    out_df = df[group_cols + all_variables].reset_index(drop=True)

    if fill_groups:
        all_groups = [list(out_df[c].unique()) for c in group_cols]
        all_groups = list(product(*all_groups))

        filled_df = pd.DataFrame(data = all_groups,
                                 columns = group_cols)

        out_df = pd.merge(filled_df, out_df, how='left', on=list(groups.keys()))

    return out_df

def get_groups(df = None,
               variables = {},
               groups = {}):
    '''
    Given the dictionaries with variables and groups, isolate variables that need to be evaluated
    after grouping and flatten (eventual) lists of variables.

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe (used if one of the groups/variables is the index)
    variables : dict
        variables dictionary (name:expr or name:list(expr))
    groups : dict
        groups dictionary (name:expr)

    Returns
    -------
    data_groups : dict
        groups dictionary (name:expr)
    data_variables :  dict
        variables dictionary (name:expr)
    delayed_variables : dict
        delayed variables dictionary (name:expr)

    '''

    # define groups
    data_groups={}

    for group, expr in groups.items():

        if (expr=='.index') & (df is not None):
            if df.index.name is None:
                df.index.name = group

            data_groups[group] = df.index.name
            df.reset_index(inplace=True)

        else:
            if expr is not None:
                data_groups[group] = expr

    # define variables
    data_variables={}
    for var, expr in variables.items():

        if isinstance(expr, list):
            # there are multiple vars to be evaluated
            for i, var_expr in enumerate(expr):
                if var_expr is not None:
                    data_variables['{}_{}'.format(var, i)] = var_expr
        else:
            # define vars dictionary
            if expr is not None:
                data_variables[var]=expr

    # delayed evaluation
    delayed_variables ={}
    to_remove = []
    for var, expr in data_variables.items():
        if DELAYED_VARIABLES_KEY in expr:
            delayed_variables[var] = expr.replace(DELAYED_VARIABLES_KEY,'')
            to_remove.append(var)

    # remove delayed variables
    for var in to_remove:
        data_variables.pop(var, None)

    return data_groups, data_variables, delayed_variables