from unittest import TestCase
from phi.flow import *
from phi.math._shape import *
from phi.math._tensor_initializers import zero
from phi.math._tensors import tensor, TensorStack

import numpy as np


class TestTensors(TestCase):

    def test_define_shapes(self):
        self.assertEqual('(2)', repr(define_shape(2)))
        self.assertEqual('(1, 2, 3)', repr(define_shape((1, 2, 3))))
        self.assertEqual('(batch=10)', repr(define_shape(batch=10)))
        self.assertEqual('(batch=10, time=5)', repr(define_shape(batch={'batch': 10, 'time': 5})))
        self.assertEqual('(batch=10, 2, 1)', repr(define_shape((2, 1), 10)))
        physics_config.x_first()
        self.assertEqual('(y=4, z=5, x=3)', repr(define_shape(y=4, z=5, x=3)))
        self.assertEqual('(batch=10, z=5, x=3, y=4, 3)', repr(define_shape(3, z=5, x=3, batch=10, y=4)))
        self.assertEqual((10, 4, 5, 3, 3), define_shape(3, y=4, z=5, x=3, batch=10).sizes)
        self.assertEqual(('batch', 'y', 'z', 'x', 0), define_shape(3, y=4, z=5, x=3, batch=10).names)

    def test_tensor_creation(self):
        v = tensor(np.ones([1, 4, 3, 2]))
        self.assertEqual((4, 3, 2), v.shape.sizes)
        v = tensor(np.ones([10, 4, 3, 2]))
        self.assertEqual((10, 4, 3, 2), v.shape.sizes)
        scalar = tensor(np.ones([1, 4, 3, 1]))
        self.assertEqual((4, 3), scalar.shape.sizes)
        a = tensor([1, 2, 3])
        self.assertEqual((3,), a.shape.sizes)

    def test_dimension_types(self):
        physics_config.x_first()
        v = tensor(np.ones([10, 4, 3, 2]))
        self.assertEqual(v.x.index, 1)
        self.assertEqual(v.x.name, 'x')
        self.assertTrue(v.x.is_spatial)
        self.assertTrue(v.batch.is_batch)
        b = v.x.as_batch()
        self.assertTrue(b.x.is_batch)

    def test_native_unstack(self):
        physics_config.x_first()
        v = tensor(np.ones([10, 4, 3, 2]))
        vx, vy = v.unstack()
        self.assertEqual('(batch=10, x=4, y=3)', repr(vx.shape))
        self.assertEqual(4, len(v.x.unstack()))
        self.assertEqual(10, len(v.batch.unstack()))

    def test_native_slice(self):
        physics_config.x_first()
        v = tensor(np.ones([1, 4, 3, 2]))
        self.assertEqual('(x=4, y=3)', repr(v[0].shape))
        self.assertEqual('(y=2, 2)', repr(v.y[0:2].x[0].shape))

    def test_native_constant_ops(self):
        v = tensor(np.ones([1, 4, 3, 2]))
        (v + 1).assert_close(2)
        (v * 3.).assert_close(3)
        (v / 2).assert_close(0.5)
        (v ** 2).assert_close(1)
        (2 ** v).assert_close(2)
        (v + [0, 1]).assert_close([1, 2])

    def test_native_native_ops(self):
        v = tensor(np.ones([1, 4, 3, 2]))
        d = v.unstack()[0]
        (v + d).assert_close(2, (d + v))
        (v * d).assert_close(1)

    def test_math_functions(self):
        v = tensor(np.ones([1, 4, 3, 2]))
        math.maximum(0, v).assert_close(1)
        math.maximum(0, -v).assert_close(0)

    def test_stacked_shapes(self):
        physics_config.x_last()
        t0 = tensor(np.ones([10, 4, 3, 2]))
        for dim in t0.dimensions:
            tensors = dim.unstack()
            stacked = TensorStack(tensors, dim.name, dim.dim_type)
            self.assertEqual(set(t0.shape.names), set(stacked.shape.names))
            self.assertEqual(t0.shape.volume, stacked.shape.volume)

    def test_stacked_native(self):
        physics_config.x_last()
        t0 = tensor(np.ones([10, 4, 3, 2]))
        tensors = t0.unstack()
        stacked = TensorStack(tensors, 0, CHANNEL_DIM)
        stacked.assert_close(t0)
        self.assertEqual((10, 4, 3, 2), stacked.native().shape)
        self.assertEqual((3, 4, 2, 10), stacked.native(order=('x', 'y', 0, 'batch')).shape)
        self.assertEqual((2, 10, 4, 3), stacked.native(order=(0, 'batch', 'y', 'x')).shape)  # this should re-stack since only the stacked dimension position is different

    def test_stacked_get(self):
        physics_config.x_first()
        t0 = tensor(np.ones([10, 4, 3, 2]))
        tensors = t0.unstack()
        stacked = TensorStack(tensors, 0, CHANNEL_DIM)
        self.assertEqual(tensors, stacked.unstack())
        assert tensors[0] is stacked[0]
        assert tensors[1] is stacked[1:2].unstack()[0]
        self.assertEqual(4, len(stacked.x.unstack()))






# print(a)
# print(tuple(a.shape))
# print(a[0])
# print(a[0:1])
# a2 = a + a
# print(a2)
# a3 = a2 + np.ones([1, 4, 3, 2])
# print(a3)
# a4 = a3 + 1
# print(a4)
# # print(a4.native())
#
# print(abs(a4).native()[0,0,0,0])
# print((-a4).native()[0,0,0,0])
# print(reversed(a4).native()[0,0,0,0])

# print(a.x[0])



# density = CenteredGrid(tensor(np.zeros([10, 4, 3, 1])))
# density += 1
#
# velocity = StaggeredGrid(tensor(np.zeros([10, 5, 4, 1])))


