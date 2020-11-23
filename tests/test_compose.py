import random
import unittest

import numpy as np
import torch
from numpy.testing import assert_almost_equal, assert_array_equal

from torch_audiomentations import PolarityInversion, Compose, PeakNormalization, Gain
from torch_audiomentations.utils.dsp import convert_decibels_to_amplitude_ratio


class TestCompose(unittest.TestCase):
    def test_compose(self):
        samples = np.array([[[1.0, 0.5, -0.25, -0.125, 0.0]]], dtype=np.float32)
        sample_rate = 16000

        augment = Compose(
            [
                Gain(min_gain_in_db=-6.000001, max_gain_in_db=-6, p=1.0),
                PolarityInversion(p=1.0),
            ]
        )
        processed_samples = augment(
            samples=torch.from_numpy(samples), sample_rate=sample_rate
        ).numpy()
        expected_factor = -convert_decibels_to_amplitude_ratio(-6)
        assert_almost_equal(
            processed_samples,
            expected_factor
            * np.array([[[1.0, 0.5, -0.25, -0.125, 0.0]]], dtype=np.float32),
            decimal=6,
        )
        self.assertEqual(processed_samples.dtype, np.float32)

    def test_compose_with_p_zero(self):
        samples = np.array([[[1.0, 0.5, -0.25, -0.125, 0.0]]], dtype=np.float32)
        sample_rate = 16000

        augment = Compose(
            transforms=[
                Gain(min_gain_in_db=-6.000001, max_gain_in_db=-6, p=1.0),
                PolarityInversion(p=1.0),
            ],
            p=0.0,
        )
        processed_samples = augment(
            samples=torch.from_numpy(samples), sample_rate=sample_rate
        ).numpy()
        assert_array_equal(samples, processed_samples)

    def test_freeze_and_unfreeze_parameters(self):
        torch.manual_seed(42)

        samples = np.array([[[1.0, 0.5, -0.25, -0.125, 0.0]]], dtype=np.float32)
        sample_rate = 16000

        augment = Compose(
            transforms=[
                Gain(min_gain_in_db=-16.000001, max_gain_in_db=-2, p=1.0),
                PolarityInversion(p=1.0),
            ]
        )

        processed_samples1 = augment(
            samples=torch.from_numpy(samples), sample_rate=sample_rate
        ).numpy()
        augment.freeze_parameters()
        processed_samples2 = augment(
            samples=torch.from_numpy(samples), sample_rate=sample_rate
        ).numpy()
        assert_array_equal(processed_samples1, processed_samples2)

        augment.unfreeze_parameters()
        processed_samples3 = augment(
            samples=torch.from_numpy(samples), sample_rate=sample_rate
        ).numpy()
        self.assertNotEqual(processed_samples1[0, 0, 0], processed_samples3[0, 0, 0])

    def test_shuffle(self):
        random.seed(42)
        samples = np.array([[[1.0, 0.5, -0.25, -0.125, 0.0]]], dtype=np.float32)
        sample_rate = 16000

        augment = Compose(
            transforms=[
                Gain(min_gain_in_db=-18.0, max_gain_in_db=-16.0, p=1.0),
                PeakNormalization(p=1.0),
            ],
            shuffle=True,
        )
        num_peak_normalization_last = 0
        num_gain_last = 0
        for i in range(100):
            processed_samples = augment(
                samples=torch.from_numpy(samples), sample_rate=sample_rate
            ).numpy()

            # Either PeakNormalization or Gain was applied last
            if processed_samples[0, 0, 0] < 0.2:
                num_gain_last += 1
            elif processed_samples[0, 0, 0] == 1.0:
                num_peak_normalization_last += 1
            else:
                raise AssertionError("Unexpected value!")

        self.assertGreater(num_peak_normalization_last, 10)
        self.assertGreater(num_gain_last, 10)
