import logging
from saport.simplex.model import Model 

def create_model() -> Model:
    model = Model(__file__)

    #TODO:
    # fill missing test based on the example_01_solvable.py
    # to make the test a bit more interesting:
    # * minimize the objective (so the solver would have to normalize it)
    # * make some ">=" constraints (GE)
    # * the model still has to be solvable by the basix simplex withour artificial var
    model = Model(__file__)

    x1 = model.create_variable("x1")
    x2 = model.create_variable("x2")

    model.add_constraint(x1 >= -98)
    model.add_constraint(x2 <= 67)
    model.add_constraint(2 * x1 + x2 <= 10)

    # minimize
    # z: 2 * x1 + 3 * x2;
    #
    # subject
    # to
    # c12: 2 * x1 + x2 >= 10000;
    # subject
    # to
    # c13: x1 >= 978;
    # subject
    # to
    # c14: x2 >= 657;

    model.minimize(3 * x1 + 3 * x2)

    return model 

def run():
    #TODO:
    # add a test "assert something" based on the example_01_solvable.py
    # TIP: you may use other solvers (e.g. https://online-optimizer.appspot.com)
    #      to find the correct solution
    model = create_model()

    try:
        solution = model.solve()
    except:
        raise AssertionError("This problem has a solution and your algorithm hasn't found it!")

    logging.info(solution)

    assert (solution.assignment(model) == [0, 0]), "Your algorithm found an incorrect solution!"

    logging.info("Congratulations! This solution seems to be alright :)")
    logging.info("This test is empty but it shouldn't be, fix it!")
    # raise AssertionError("Test is empty")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    run()
