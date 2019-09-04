
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/11a_transfer_learning_my_reimplementation.ipynb

from exports.nb_11 import *

def random_splitter(fn, p_valid): return random.random() < p_valid

class AdaptiveConcatPool2d(nn.Module):
    def __init__(self, size=1):
        super().__init__()
        self.output_size = size
        self.avg_pool = nn.AdaptiveAvgPool2d(size)
        self.max_pool = nn.AdaptiveMaxPool2d(size)

    def forward(self, x): return torch.cat([self.max_pool(x), self.avg_pool(x)], dim=1)

def adapt_model(learner, data):
    cut = next(i for i, o in enumerate(learner.model.children()) if isinstance(o, nn.AdaptiveAvgPool2d))
    bottleneck_model = learner.model[:cut]
    xb, yb = get_batch(data.valid_dl, learner)
    pred = bottleneck_model(xb)
    n_in = pred.shape[1]
    model_new = nn.Sequential(bottleneck_model,
                              AdaptiveConcatPool2d(),
                              Flatten(),
                              nn.Linear(n_in*2, data.channels_out))
    learner.model = model_new

def sched_1cycle(lrs, pct_start=0.3, mom_start=0.95, mom_mid=0.85, mom_end=0.95):
    phases = create_phases(pct_start)
    sched_lr = [combine_scheds(phases, cos_1cycle_anneal(lr/10., lr, lr/1e5))
                for lr in lrs]
    sched_mom = combine_scheds(phases, cos_1cycle_anneal(mom_start, mom_mid, mom_end))
    return [ParamScheduler('lr', sched_lr),
            ParamScheduler('mom', sched_mom)]

class DebugCallback(Callback):
    _order = 999
    def __init__(self, cb_name, f=None): self.cb_name, self.f = cb_name, f
    def __call__(self, cb_name):
        if cb_name == self.cb_name:
            # If a function, f, is passed, then execute it.
            if self.f: self.f(self.run)
            # Otherwise set a normal debug trace.
            else: set_trace()

from types import SimpleNamespace
cb_types = SimpleNamespace(**{o:o for o in Learner.ALL_CALLBACKS})