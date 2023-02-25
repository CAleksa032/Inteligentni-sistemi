import copy


class Algorithm:
    def get_algorithm_steps(self, tiles, variables, words):
        pass


class ExampleAlgorithm(Algorithm):

    def get_algorithm_steps(self, tiles, variables, words):
        moves_list = [['0h', 0], ['0v', 2], ['1v', 1], ['2h', 1], ['4h', None],
                 ['2h', None], ['1v', None], ['0v', 3], ['1v', 1], ['2h', 1],
                 ['4h', 4], ['5v', 5]]
        domains = {var: [word for word in words] for var in variables}
        solution = []
        for move in moves_list:
            solution.append([move[0], move[1], domains])
        return solution


def get_indexes(index, dim):
    indexes = [index[-1]]
    index = index.rstrip(index[-1])
    indexes.append(int(index) // dim)
    indexes.append(int(index) % dim)
    return indexes


def is_consistent_assignment(v, val, variables, domains, constraints):
    if len(domains[v]) < 1:
        return False
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! len(val) treba da se smisli da se prkeo variables[v] ali ovo mi nije to variables
    tmp = {i: 0 for i in range(variables[v])}
    indexes = get_indexes(v, len(constraints[0]))
    for i in range(variables[v]):
        if indexes[0] == "v":
            tmp[i] = constraints[indexes[1] + i][indexes[2]][-1]
        elif indexes[0] == "h":
            tmp[i] = constraints[indexes[1]][indexes[2] + i][-1]
    for tmp_char in range(len(val)):
        if tmp[tmp_char] == 0:
            continue
        if tmp[tmp_char] != val[tmp_char]:
            return False
    return True


def update_constraints(constraints, val, v, cnt):
    indexes = get_indexes(v, len(constraints[0]))
    for i in range(cnt):
        if indexes[0] == "v":
            (constraints[indexes[1] + i][indexes[2]]).append(val[i])
        elif indexes[0] == "h":
            (constraints[indexes[1]][indexes[2] + i]).append(val[i])


def backtrack_search(variables_dict, domains, solution, lvl, constraints, steps):
    variables = []
    for var in variables_dict:
        variables.append(var)
        solution.append(None)
    if lvl == len(variables):
        return True
    v = variables[lvl]
    for val in domains[v]:
        if is_consistent_assignment(v, val, variables_dict, domains, constraints):
            # prosiriti solution da pravilno vraca vrednost
            solution[variables.index(v)] = val
            steps.append([v, domains[v].index(val), domains])
            new_constraints = copy.deepcopy(constraints)
            update_constraints(new_constraints, val, v, variables_dict[v])
            new_dom = copy.deepcopy(domains)
            #new_dom[v] = [val]
            if backtrack_search(variables_dict, new_dom, solution, lvl+1, new_constraints, steps):
                return True
            solution[variables.index(v)] = None
    steps.append([v, None, domains])
    return False


def make_working_matrix(tiles):
    tmp_matrix = []
    for i in range(len(tiles)):
        tmp_matrix.append([])
        for j in range(len(tiles[0])):
            tmp_matrix[i].append([])
            if tiles[i][j]:
                tmp_matrix[i][j].append(1)
            else:
                tmp_matrix[i][j].append(0)
    return tmp_matrix


def populate_constraint_matrix(variables, tiles):
    tmp_matrix = make_working_matrix(tiles)
    dim = len(tiles[0])
    for var in variables:
        indexes = get_indexes(var, dim)
        for i in range(variables[var]):
            if indexes[0] == "v":
                (tmp_matrix[indexes[1] + i][indexes[2]]).append(var)
            elif indexes[0] == "h":
                (tmp_matrix[indexes[1]][indexes[2] + i]).append(var)
    return tmp_matrix


def populate_domains(variables, words):
    return {var: [word for word in words if len(word) == variables[var]] for var in variables}


class Backtracking(Algorithm):

    def get_algorithm_steps(self, tiles, variables, words):
        domains = populate_domains(variables, words)
        #con = make_working_matrix(tiles)
        #update_constraints(con, "ra", "0h", 2)
        #update_constraints(con, "ka", "4h", 2)
        #a = is_consistent_assignment("0v", "rat", variables, domains, con)
        solution = []
        steps = []
        backtrack_search(variables, domains, solution, 0, make_working_matrix(tiles), steps)
        return steps


def are_constrained(v, var, constraints, cnt):
    tmp = set()
    indexes = get_indexes(v, len(constraints[0]))
    for i in range(cnt):
        if indexes[0] == "v":
            for j in range(len(constraints[indexes[1] + i][indexes[2]])):
                if j != 0:
                    tmp.add(constraints[indexes[1] + i][indexes[2]][j])
        elif indexes[0] == "h":
            for j in range(len(constraints[indexes[1]][indexes[2] + i])):
                if j != 0:
                    tmp.add(constraints[indexes[1]][indexes[2] + i][j])
    if var in tmp:
        return True
    else:
        return False


def update_domain(domains, v, var, val, constraints, variables):
    tmp_domain = []
    for word in domains[var]:
        if is_consistent_assignment(var, word, variables, domains, constraints):
            tmp_domain.append(word)
    domains[var] = tmp_domain
    return domains


def backtrack_search_fc(variables_dict, domains, solution, lvl, constraints, steps, constraint_key):
    variables = []
    for var in variables_dict:
        variables.append(var)
        solution.append(None)
    if lvl == len(variables):
        return True
    v = variables[lvl]
    for val in domains[v]:
        if is_consistent_assignment(v, val, variables_dict, domains, constraints):
            solution[variables.index(v)] = val
            steps.append([v, domains[v].index(val), domains])
            new_constraints = copy.deepcopy(constraints)
            update_constraints(new_constraints, val, v, variables_dict[v])
            new_dom = copy.deepcopy(domains)
            # new_dom[v] = [val]
            do = True
            for var in variables_dict:
                if var != v and are_constrained(v, var, constraint_key, variables_dict[v]):
                    new_dom = update_domain(new_dom, v, var, val, new_constraints, variables_dict)
                    if len(new_dom[var]) == 0:
                        do = False
            if do and backtrack_search_fc(variables_dict, new_dom, solution, lvl+1, new_constraints, steps, constraint_key):
                return True
            solution[variables.index(v)] = None
    steps.append([v, None, domains])
    return False


class ForwardChecking(Algorithm):
    def get_algorithm_steps(self, tiles, variables, words):
        domains = populate_domains(variables, words)
        constraint_key = populate_constraint_matrix(variables, tiles)
        tmp = are_constrained("0v", "2h", constraint_key, 3)
        solution = []
        steps = []
        backtrack_search_fc(variables, domains, solution, 0, make_working_matrix(tiles), steps, constraint_key)
        return steps


def get_all_arcs(variables, domains, constraints):
    tmp = []
    for i in variables:
        for j in variables:
            if i == j:
                continue
            if are_constrained(i, j, constraints,variables[i]):
                tmp.append((i, j))
    return tmp


def satisfies_constraint (val_x, val_y, x, y, constraints):
    index_x = get_indexes(x, len(constraints[0]))
    index_y = get_indexes(y, len(constraints[0]))
    if index_x[0] == "h":
        first = index_x
        second = index_y
        first_word = val_x
        second_word = val_y
    else:
        first = index_y
        second = index_x
        first_word = val_y
        second_word = val_x
    first_char_pos = abs(first[2] - second [2])
    second_char_pos = abs(first[1] - second[1])
    if first_word[first_char_pos] == second_word[second_char_pos]:
        return True
    else:
        return False


def arc_consistency(variables, domains, constraints, constraint_key):
    arc_list = get_all_arcs(variables, domains, constraint_key)
    while arc_list:
        x, y = arc_list.pop(0)
        x_vals_to_del = []
        for val_x in domains[x]:
            y_no_val = True
            for val_y in domains[y]:
                if satisfies_constraint(val_x, val_y, x, y, constraints):
                    y_no_val = False
                    break
            if y_no_val:
                x_vals_to_del.append(val_x)
        if x_vals_to_del:
            domains[x] = [v for v in domains[x] if v not in x_vals_to_del]
            if not domains[x]:
                return False
            for v in variables:
                if v != x and are_constrained(v, x, constraints, variables[v]):
                    arc_list.append((v, x))
    return True


def backtrack_search_fc_ac(variables_dict, domains, solution, lvl, constraints, steps, constraint_key):
    variables = []
    for var in variables_dict:
        variables.append(var)
        solution.append(None)
    if lvl == len(variables):
        return True
    v = variables[lvl]
    for val in domains[v]:
        if is_consistent_assignment(v, val, variables_dict, domains, constraints):
            solution[variables.index(v)] = val
            steps.append([v, domains[v].index(val), domains])
            new_constraints = copy.deepcopy(constraints)
            update_constraints(new_constraints, val, v, variables_dict[v])
            new_dom = copy.deepcopy(domains)
            # new_dom[v] = [val]
            do = True
            for var in variables_dict:
                if var != v and are_constrained(v, var, constraint_key, variables_dict[v]):
                    new_dom = update_domain(new_dom, v, var, val, new_constraints, variables_dict)
                    if len(new_dom[var]) == 0:
                        do = False
            if not arc_consistency(variables_dict, new_dom, constraints, constraint_key):
                do = False
                continue
            if do and backtrack_search_fc_ac(variables_dict, new_dom, solution, lvl+1, new_constraints, steps, constraint_key):
                return True
            solution[variables.index(v)] = None
    steps.append([v, None, domains])
    return False


class ArcConsistency(Algorithm):
    def get_algorithm_steps(self, tiles, variables, words):
        domains = populate_domains(variables, words)
        constraint_key = populate_constraint_matrix(variables, tiles)
        tmp = are_constrained("0v", "2h", constraint_key, 3)
        solution = []
        steps = []
        backtrack_search_fc_ac(variables, domains, solution, 0, make_working_matrix(tiles), steps, constraint_key)
        return steps
