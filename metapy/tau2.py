from __future__ import annotations
from typing import Literal
import numpy as np


def tausq_dl(y, vi):
    wi = 1.0 / vi
    ybar = np.sum(wi * y) / np.sum(wi)
    Q = np.sum(wi * (y - ybar) ** 2)
    df = len(y) - 1
    C = np.sum(wi) - (np.sum(wi**2) / np.sum(wi))
    tau2 = max((Q - df) / C, 0.0)
    return float(tau2), float(Q), int(df)


def tausq_pm(y, vi, tol=1e-8, maxiter=100):
    # Paule–Mandel: iteratively find tau^2 such that Q = df
    tau2 = 0.0
    df = len(y) - 1
    for _ in range(maxiter):
        wi = 1.0 / (vi + tau2)
        ybar = np.sum(wi * y) / np.sum(wi)
        Q = np.sum(wi * (y - ybar) ** 2)
        # Derivative approx (safeguarded)
        dQ = -np.sum((wi**2) * (y - ybar) ** 2) + 2 * np.sum(wi) * np.sum((wi**2) * (y - ybar)) * np.sum(wi * (y - ybar)) / (np.sum(wi) ** 2 + 1e-12)
        if abs(Q - df) < tol:
            break
        step = (Q - df) / (dQ if dQ != 0 else (np.sign(Q - df) * 1.0))
        tau2_new = tau2 - step
        if tau2_new < 0:
            tau2_new = 0.5 * tau2
        if abs(tau2_new - tau2) < tol:
            tau2 = tau2_new
            break
        tau2 = tau2_new
    tau2 = max(float(tau2), 0.0)
    return tau2


def estimate_tau2(y, vi, method: Literal["DL", "PM"] = "DL"):
    if method == "DL":
        tau2, Q, df = tausq_dl(y, vi)
        return tau2, Q, df
    elif method == "PM":
        tau2 = tausq_pm(y, vi)
        wi = 1.0 / (vi + tau2)
        ybar = np.sum(wi * y) / np.sum(wi)
        Q = float(np.sum(wi * (y - ybar) ** 2))
        df = len(y) - 1
        return tau2, Q, df
    else:
        raise ValueError(f"Unknown method: {method}. Use 'DL' or 'PM'.")