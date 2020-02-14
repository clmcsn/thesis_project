import numpy as np

from pymoo.algorithms.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.model.problem import Problem

network_name = "vgg11bn"
config_fname="{}.mc".format(network_name)
maskTimingCharFile="../reports/maskTimingCharact_csaMult_0nsClk.txt"

#fetching the characterization mask
print("Fetching mask characterization from {}...\n".format(maskTimingCharFile))
mask_charact_dict = get_mask_hwCharact(maskTimingCharFile)
#it is important to sort dictionary for simplify the code later.
#during the characterization there wouldn't be the need to check for dominated solutions
#in the table
mask_charact_dict = {k: v for k, v in sorted(mask_charact_dict.items(), key=lambda item: item[1])}


