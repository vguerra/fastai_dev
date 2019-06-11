#AUTOGENERATED! DO NOT EDIT! File to edit: dev/08_augmentation.ipynb (unless otherwise specified).

__all__ = ['flip_affine', 'mask_tensor', 'DihedralAffine']

from ..imports import *
from ..test import *
from ..core import *
from .pipeline import *
from .source import *
from .core import *
from ..vision.core import *
from .external import *

import math
from torch import stack, zeros_like as t0, ones_like as t1
from torch.distributions.bernoulli import Bernoulli

def flip_affine(x, p=0.5):
    "Flip as an affine transform"
    mask = -2*x.new_empty(x.size(0)).bernoulli_(p)+1
    return stack([stack([mask,     t0(mask), t0(mask)], dim=1),
                  stack([t0(mask), t1(mask), t0(mask)], dim=1),
                  stack([t0(mask), t0(mask), t1(mask)], dim=1)], dim=1)

def mask_tensor(x, p=0.5, neutral=0.):
    "Mask elements of `x` with probability `p` by replacing them with `neutral`"
    if p==1.: return x
    if neutral != 0: x.add_(-neutral)
    mask = x.new_empty(*x.size()).bernoulli_(p)
    x.mul_(mask)
    return x.add_(neutral) if neutral != 0 else x

class DihedralAffine():
    "Dihedral as an affine transform"
    def __init__(self, p=0.5): self.p=p

    def randomize(self, x):
        idx = mask_tensor(torch.randint(0, 8, (x.size(0),), device=x.device), p=self.p)
        xs = 1 - 2*(idx & 1)
        ys = 1 - (idx & 2)
        m0,m1 = (idx<4).long(),(idx>3).long()
        self.mat = stack([stack([xs*m0,  xs*m1,  t0(xs)], dim=1),
                          stack([ys*m1,  ys*m0,  t0(xs)], dim=1),
                          stack([t0(xs), t0(xs), t1(xs)], dim=1)], dim=1).float()

    def __call__(self): return self.mat