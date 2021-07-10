#!/usr/bin/python

import argparse
import numpy
import matplotlib.pyplot as plt
from PicoNuclear.pico3000a import PicoScope3000A
import PicoNuclear.tools as tools


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=argparse.FileType('r'), 
                         help='XML configuration file')
    parser.add_argument('--save', help='Name of output file with waveforms')

    args = parser.parse_args()

    config = tools.load_configuration(args.config)
    s = PicoScope3000A()

    s.set_channel('A', coupling_type=config['A']['coupling'], 
            range_value=config['A']['range'], offset=config['A']['offset'])
    s.set_channel('B', coupling_type=config['B']['coupling'], 
            range_value=config['B']['range'], offset=config['B']['offset'])
    s.set_trigger(config['trigger']['source'],
                  threshold=config['trigger']['threshold'],
                  direction=config['trigger']['direction'], 
                  auto_trigger=config['trigger']['autotrigger'])
    print('# Interval is', s.get_interval_from_timebase(config['timebase'], 
        config['pre'] + config['post']), 'ns')

    t, [A, B] = s.measure_relative_adc(config['pre'], config['post'],
            num_captures=config['captures'], timebase=config['timebase'], 
            inverse=True)

    s.close()

    if args.save is not None:
        data = numpy.zeros((A.shape[1], A.shape[0] + B.shape[0] + 1))
        data[:, 0] = t
        data[:, 1:A.shape[0]+1] = numpy.rot90(A)
        data[:, A.shape[0]+1: ] = numpy.rot90(B)
        numpy.savetxt('{}.txt'.format(args.save), data, 
                fmt='%.3f', delimiter=' ')

    nx = int(numpy.round(numpy.sqrt(config['captures'])))
    ny = int(numpy.ceil(config['captures'] / nx))

    fig = plt.figure(1, (8, 8))

    for i, Ai in enumerate(A):
        ax = plt.subplot(nx, ny, i + 1)
        ax.plot(t, A[i, :], ds='steps-mid', color='blue', label='A')
        ax.plot(t, B[i, :], ds='steps-mid', color='red', label='B')
        ax.set_ylim(-config['A']['range'] - config['A']['offset'],
                config['A']['offset'])
        ax.set_xlabel('t (ns)')
        ax.set_ylabel('U (V)')

    ax.legend()
    fig.set_size_inches(8, 8)
    fig.tight_layout()
    plt.show()

