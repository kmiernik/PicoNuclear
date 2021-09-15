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
    parser.add_argument('--save', 
            help='Name of output file with waveforms (optional)')
    parser.add_argument('-f', help='Apply trapezoidal filter (optional)',
            action='store_true')

    args = parser.parse_args()

    config = tools.load_configuration(args.config)
    s = PicoScope3000A()

    s.set_channel('A', coupling_type=config['A']['coupling'], 
            range_value=config['A']['range'], offset=config['A']['offset'])
    s.set_trigger(config['trigger']['source'],
                  threshold=config['trigger']['threshold'],
                  direction=config['trigger']['direction'], 
                  auto_trigger=config['trigger']['autotrigger'])
    interval = s.get_interval_from_timebase(config['timebase'], 
                                    config['pre'] + config['post'])

    if interval >= 1000:
        unit = [1000000, 'ms']
    elif interval >= 10:
        unit = [1000, 'us']
    else:
        unit = [1, 'ns']
    print('# Interval is {} {} ({} {})'.format(interval, 'ns', 
                                            interval / unit[0], unit[1]))
    print('# Range is {} {}'.format( (config['pre'] + config['post'] 
                                       * interval / unit[0]),
                                       unit[1]))

    t, [A, B] = s.measure(config['pre'], config['post'],
            num_captures=config['captures'], timebase=config['timebase'])

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

    if nx <= 1:
        nx = 2
    if ny <= 1:
        ny = 2

    fig, axes = plt.subplots(nx, ny, sharex='all', sharey='all')

    for i, Ai in enumerate(A):
        ix = int(i % nx)
        iy = int(i // nx)
        axes[ix][iy].plot(t / unit[0], A[i, :], marker='.', ls='-', 
                ds='steps-mid', color='blue', label='A')
        if args.f:
            amp, sa = tools.trapezoidal(A[i, :], config['A'], interval)
            ta = tools.zero_crossing(A[i, :], config['A']['filter']['B'], 
                                    falling=False)
            axes[ix][iy].axvline(ta / unit[0], ls='--', color='red')
            axes[ix][iy].text(ta / unit[0], 0, 
                    ' A = {:.1f}\n t = {:.1f}'.format(amp[0], ta / unit[0]),
                    fontsize=8)


    for ax in axes[-1]:
        ax.set_xlabel('t ({})'.format(unit[1]), size=14)
    for axr in axes:
        axr[0].set_ylabel('U (V)', size=14)
        axr[0].set_ylim(-config['A']['range'] + config['A']['offset'],
                config['A']['range'] + config['A']['offset'])
        axr[0].set_xlim(0, None)
        for ax in axr:
            ax.legend()
            ax.tick_params(axis='both', labelsize=12)

    fig.set_size_inches(12, 9)
    fig.tight_layout()
    plt.show()

