from itertools import islice, count
from operator import itemgetter

import typing
from typing import List, Iterable, Optional, Callable, Any

from AnyQt.QtGui import QColor, QRadialGradient, QPainterPathStroker


if typing.TYPE_CHECKING:
    T = typing.TypeVar("T")
    A = typing.TypeVar("A")
    B = typing.TypeVar("B")
    C = typing.TypeVar("C")


def composition(f, g):
    # type: (Callable[[A], B], Callable[[B], C]) -> Callable[[A], C]
    """Return a composition of two functions
    """
    def fg(arg):  # type: (A) -> C
        return g(f(arg))
    return fg


def argsort(iterable, key=None, reverse=False):
    # type: (Iterable[T], Optional[Callable[[T], Any]], bool) -> List[int]
    if key is None:
        key_ = itemgetter(0)
    else:
        key_ = composition(itemgetter(0), key)
    ordered = sorted(zip(iterable, count(0)), key=key_, reverse=reverse)
    return list(map(itemgetter(1), ordered))


def linspace_(count):
    # type: (int) -> Iterable[float]
    if count > 1:
        return (i / (count - 1) for i in range(count))
    elif count == 1:
        return (_ for _ in (0.0,))
    elif count == 0:
        return (_ for _ in ())
    else:
        raise ValueError("Count must be non-negative")


def linspace(count):
    """Return `count` evenly spaced points from 0..1 interval excluding
    both end points, e.g. `linspace(3) == [0.25, 0.5, 0.75]`.
    """
    return list(islice(linspace_(count + 2), 1, count + 1))


def sample_path(path, num=10):
    """Sample `num` equidistant points from the `path` (`QPainterPath`).
    """
    return [path.pointAtPercent(p) for p in linspace_(num)]


def saturated(color, factor=150):
    """Return a saturated color.
    """
    h = color.hsvHueF()
    s = color.hsvSaturationF()
    v = color.valueF()
    a = color.alphaF()
    s = factor * s / 100.0
    s = max(min(1.0, s), 0.0)
    return QColor.fromHsvF(h, s, v, a).convertTo(color.spec())


def radial_gradient(color, color_light=50):
    """
    radial_gradient(QColor, QColor)
    radial_gradient(QColor, int)

    Return a radial gradient. `color_light` can be a QColor or an int.
    In the later case the light color is derived from `color` using
    `saturated(color, color_light)`.

    """
    if not isinstance(color_light, QColor):
        color_light = saturated(color, color_light)
    gradient = QRadialGradient(0.5, 0.5, 0.5)
    gradient.setColorAt(0.0, color_light)
    gradient.setColorAt(0.5, color_light)
    gradient.setColorAt(1.0, color)
    gradient.setCoordinateMode(QRadialGradient.ObjectBoundingMode)
    return gradient


def toGraphicsObjectIfPossible(item):
    """Return the item as a QGraphicsObject if possible.

    This function is intended as a workaround for a problem with older
    versions of PyQt (< 4.9), where methods returning 'QGraphicsItem *'
    lose the type of the QGraphicsObject subclasses and instead return
    generic QGraphicsItem wrappers.

    """
    if item is None:
        return None

    obj = item.toGraphicsObject()
    return item if obj is None else obj


def uniform_linear_layout(points):
    """Layout the points (a list of floats in 0..1 range) in a uniform
    linear space while preserving the existing sorting order.

    """
    indices = argsort(points)
    space = linspace(len(points))
    # invert the indices
    indices = invert_permutation_indices(indices)
    return [space[i] for i in indices]


def invert_permutation_indices(indices):
    """Invert the permutation giver by indices.
    """
    inverted = [0] * len(indices)
    for i, index in enumerate(indices):
        inverted[index] = i
    return inverted


def stroke_path(path, pen):
    """Create a QPainterPath stroke from the `path` drawn with `pen`.
    """
    stroker = QPainterPathStroker()
    stroker.setCapStyle(pen.capStyle())
    stroker.setJoinStyle(pen.joinStyle())
    stroker.setMiterLimit(pen.miterLimit())
    stroker.setWidth(max(pen.widthF(), 1e-9))

    return stroker.createStroke(path)
