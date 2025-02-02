import numpy as np
import scipy.integrate as scp_int

from SciDataTool.Functions import AxisError


def antiderivate(values, ax_val, index, Nper, is_aper, is_phys, is_freqs):
    """Returns the anti-derivate of values along given axis
    values is assumed to be periodic and axis is assumed to be a linspace

    Parameters
    ----------
    values: ndarray
        array to derivate
    ax_val: ndarray
        axis values
    index: int
        index of axis along which to derivate
    Nper: int
        number of periods to replicate
    is_aper: bool
        True if values is anti-periodic along axis
    is_phys: bool
        True if physical quantity (time/angle/z)
    is_freqs: bool
        True if frequency axis

    Returns
    -------
    values: ndarray
        anti-derivate of values
    """

    if is_freqs:
        dim_array = np.ones((1, values.ndim), int).ravel()
        dim_array[index] = -1
        axis_reshaped = ax_val.reshape(dim_array)
        values = values / (axis_reshaped * 2 * 1j * np.pi)

    elif is_phys:

        if ax_val.size > 1:
            # Add last point to axis
            ax_full = np.concatenate(
                (
                    ax_val,
                    np.array([ax_val[-1] + ax_val[1] - ax_val[0]]),
                )
            )
            # Swap axis to always have anti-derivating axis on 1st position
            shape = list(values.shape)
            values = np.swapaxes(values, index, 0)
            shape[index], shape[0] = shape[0], shape[index]
            # Get values on a full (anti-)period
            shape[0] = shape[0] + 1
            values_full = np.zeros(shape, dtype=values.dtype)
            values_full[:-1, ...] = values
            # Add first sample at the end of values to integrate on last interval
            # Last value is the same as (respectively the opposite of) the first value
            # in case of periodicity (respectively anti-periodicity)
            values_full[-1, ...] = (-1) ** int(is_aper) * values[0, ...]
            # Anti-derivate along axis
            values = np.roll(
                scp_int.cumulative_trapezoid(values_full, x=ax_full, axis=0),
                shift=1,
                axis=0,
            )
            # Integration constant is given by removing average value
            values = values - np.mean(values, axis=0)
            # Get N first values and swap axes back to origin
            values = np.swapaxes(values, 0, index)

        else:
            raise Exception("Cannot anti-derivate along axis if axis size is 1")

    else:
        raise AxisError("Derivation only available for time/angle/z/freqs")

    return values


def integrate(values, ax_val, index, Nper, is_aper, is_phys):
    """Returns the integral of values along given axis

    Parameters
    ----------
    values: ndarray
        array to integrate
    ax_val: ndarray
        axis values
    index: int
        index of axis along which to derivate
    is_aper: bool
        True if values is anti-periodic along axis

    Returns
    -------
    values: ndarray
        integration of values
    """

    if not is_phys:
        raise AxisError("Integration only available for time/angle/z")

    if ax_val.size > 1:
        shape = list(values.shape)
        if is_aper:
            # Integration of anti-periodic signal yields zero
            shape0 = [s for ii, s in enumerate(shape) if ii != index]
            values = np.zeros(shape0, dtype=values.dtype)
        else:
            # Add last point to axis
            ax_full = np.concatenate(
                (
                    ax_val,
                    np.array([ax_val[-1] + ax_val[1] - ax_val[0]]),
                )
            )
            # Swap axis to always have integration axis on 1st position
            values = np.swapaxes(values, index, 0)
            shape[index], shape[0] = shape[0], shape[index]
            # Get values on a full (anti-)period
            shape[0] = shape[0] + 1
            values_full = np.zeros(shape, dtype=values.dtype)
            values_full[:-1, ...] = values
            # Add first sample at the end of values to integrate on last interval
            # Last value is the same as (respectively the opposite of) the first value
            # in case of periodicity (respectively anti-periodicity)
            values_full[-1, ...] = values[0, ...]
            # Integrate along axis
            values = Nper * np.trapz(values_full, x=ax_full, axis=0)
            # Get N first values and swap axes back to origin
            values = np.swapaxes(values, 0, index - 1)

    else:
        raise Exception("Cannot anti-derivate along axis if axis size is 1")

    return values


def derivate(values, ax_val, index, Nper, is_aper, is_phys, is_freqs):
    """Returns the first derivate of values along given axis
    values is assumed to be periodic and axis is assumed to be a linspace

    Parameters
    ----------
    values: ndarray
        array to derivate
    ax_val: ndarray
        axis values
    index: int
        index of axis along which to derivate
    Nper: int
        number of periods to replicate
    is_aper: bool
        True if values is anti-periodic along axis
    is_phys: bool
        True if physical quantity (time/angle/z)
    is_freqs: bool
        True if frequency axis

    Returns
    -------
    values: ndarray
        derivate of values
    """

    if is_freqs:
        dim_array = np.ones((1, values.ndim), int).ravel()
        dim_array[index] = -1
        axis_reshaped = ax_val.reshape(dim_array)
        values = values * axis_reshaped * 2 * 1j * np.pi

    elif is_phys:
        if ax_val.size > 1:
            # Create the full vector of axis values
            ax_full = np.concatenate(
                (
                    np.array([ax_val[0] - ax_val[1]]),
                    ax_val,
                    np.array([ax_val[-1] + ax_val[1] - ax_val[0]]),
                )
            )
            # Swap axis to always have derivating axis on 1st position
            shape = list(values.shape)
            values = np.swapaxes(values, index, 0)
            shape[index], shape[0] = shape[0], shape[index]
            # Get values on a full (anti-)period
            shape[0] = shape[0] + 2
            values_full = np.zeros(shape, dtype=values.dtype)
            values_full[1:-1, ...] = values
            # Add first and last samples at the end and start of values to make values_full periodic
            # Last value is the same as (respectively the opposite of) the first value
            # in case of periodicity (respectively anti-periodicity)
            values_full[-1, ...] = (-1) ** int(is_aper) * values[0, ...]
            values_full[0, ...] = (-1) ** int(is_aper) * values[-1, ...]
            # Derivate along axis
            values = np.gradient(values_full, ax_full, axis=0)
            # Get N first values and swap axes back to origin
            values = np.swapaxes(values[1:-1, ...], 0, index)

        else:
            raise Exception("Cannot derivate along axis if axis size is 1")
    else:
        raise AxisError("Derivation only available for time/angle/z/freqs")

    return values
