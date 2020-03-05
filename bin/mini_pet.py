#!/usr/bin/python
import argparse
import datetime
import numpy
import matplotlib.pyplot as plt
import PicoNuclear.tools as tools
from PicoNuclear.pico3000a import PicoScope3000A
from scipy.optimize import curve_fit

def E(x, calib):
    r = 0
    for i, c in enumerate(calib):
        r += c * x**i
    return r


def gaussian(x, x0, s, A): 
    return (A / numpy.sqrt(2 * numpy.pi * s**2) * 
            numpy.exp(-(x-x0)**2 / (2 * s**2)))


def update_plots(axes, all_lines, good_lines, all_list, good_list, 
        ch_range, t_range):
    all_data = numpy.array(all_list)
    good_data = numpy.array(good_list)
    bins, edges = numpy.histogram(all_data[:, 3] - all_data[:, 2], 
            range=(-t_range, t_range), bins=2 * t_range)
    all_lines[0][0].set_ydata(bins)
    all_lines[0][0].set_xdata(edges[:-1])
    axes[0][0].set_ylim(0, max(bins) * 1.1)
    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 3] - good_data[:, 2],
                range=(-t_range, t_range), bins= 2 * t_range)
        good_lines[0][0].set_ydata(bins)
        good_lines[0][0].set_xdata(edges[:-1])

    all_lines[1][1].set_ydata(all_data[:, 1])
    all_lines[1][1].set_xdata(all_data[:, 0])
    if len(good_data > 0):
        good_lines[1][1].set_ydata(good_data[:, 1])
        good_lines[1][1].set_xdata(good_data[:, 0])
    
    bins, edges = numpy.histogram(all_data[:, 0], range=(0, ch_range),
            bins=ch_range)
    all_lines[0][1].set_ydata(bins)
    all_lines[0][1].set_xdata(edges[:-1])
    axes[0][1].set_ylim(0, max(bins[100:]))
    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 0], range=(0, ch_range),
                        bins=ch_range)
        good_lines[0][1].set_ydata(bins)
        good_lines[0][1].set_xdata(edges[:-1])

    bins, edges = numpy.histogram(all_data[:, 1], range=(0, ch_range),
                        bins=ch_range)
    all_lines[1][0].set_ydata(bins)
    all_lines[1][0].set_xdata(edges[:-1])
    axes[1][0].set_ylim(0, max(bins[100:]))
    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 1], range=(0, ch_range),
                        bins=ch_range)
        good_lines[1][0].set_ydata(bins)
        good_lines[1][0].set_xdata(edges[:-1])

    fig.canvas.draw()
    fig.canvas.flush_events()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=argparse.FileType('r'), 
                         help='XML configuration file')
    parser.add_argument('--list', help='List mode file prefix')
    parser.add_argument('-v', '--verbose', action='store_true',
            help='Print collected events')
    parser.add_argument('-t', type=float, default=-1.0, help='Maximum run\
            time in seconds.')
    parser.add_argument('-n', type=int, default=-1, help='Number of events\
            to collect. If used with -t option than OR logic is used for two\
            conditions.')

    args = parser.parse_args()

    t_max = args.t
    n_max = args.n
    if args.t < 0 and args.n < 0:
        t_max = 5.0

    t_update = 2.0

    config = tools.load_configuration(args.config)

    plt.ion()
    fig, axes = plt.subplots(2, 2)

    all00, = axes[0][0].plot([], [], ds='steps-mid', color='black')
    good00, = axes[0][0].plot([], [], ds='steps-mid', color='red')
    axes[0][0].set_xlim(-config['t_range'], config['t_range'])
    time_text = axes[0][0].text(1.0, 0.9, '', fontsize=14, color='red')
    axes[0][0].set_xlabel('$\Delta t$')

    all11, = axes[1][1].plot([], [], 's', mfc='None', color='Black')
    good11, = axes[1][1].plot([], [], 'o', color='Red')
    axes[1][1].set_xlabel('Ch A')
    axes[1][1].set_ylabel('Ch B')
    axes[1][1].set_xlim(0, config['ch_range'])
    axes[1][1].set_ylim(0, config['ch_range'])

    all01, = axes[0][1].plot([], [], ds='steps-mid', color='black')
    good01, = axes[0][1].plot([], [], ds='steps-mid', color='blue')
    axes[0][1].set_xlabel('Ch A')
    axes[0][1].set_xlim(0, config['ch_range'])

    all10, = axes[1][0].plot([], [], ds='steps-mid', color='black')
    good10, = axes[1][0].plot([], [], ds='steps-mid', color='red')
    axes[1][0].set_xlabel('Ch B')
    axes[1][0].set_xlim(0, config['ch_range'])

    fig.set_size_inches(12, 9)
    fig.tight_layout()

    fig.canvas.draw()
    fig.canvas.flush_events()

    lines_all = [[all00, all01], [all10, all11]]
    lines_good = [[good00, good01], [good10, good11]]


    header = '* Config:\n'
    header += '\t t_max = {:.3f} s, n_max = {}\n'.format(t_max, n_max)
    for key, value in config.items():
        if isinstance(value, dict):
            header += '\t {}:\n'.format(key)
            for key2, value2 in value.items():
                header += '\t\t {} : {}\n'.format(key2, value2)
        else:
            header += '\t {} : {}\n'.format(key, value)

    s = PicoScope3000A()

    s.set_channel('A', coupling_type=config['A']['coupling'], 
            range_value=config['A']['range'], offset=config['A']['offset'])
    s.set_channel('B', coupling_type=config['B']['coupling'], 
            range_value=config['B']['range'], offset=config['B']['offset'])
    s.set_trigger(config['trigger']['source'],
                  threshold=config['trigger']['threshold'],
                  direction=config['trigger']['direction'], 
                  auto_trigger=config['trigger']['autotrigger'])

    clock = s.get_interval_from_timebase(config['timebase'], 
                                         config['pre'] + config['post'])

    t0 = datetime.datetime.now()
    dt = (datetime.datetime.now() - t0).total_seconds()

    header += 'Start at {}\n'.format(t0)
    header += 'EA  EB  tA  tB'
    print('* Start at', t0)

    all_data = []
    good_data = []
    t_plot = datetime.datetime.now()
    while True:
        try:
            t, [A, B] = s.measure_relative_adc(config['pre'], config['post'],
                                  num_captures=config['captures'],
                                  timebase=config['timebase'], 
                                  inverse=True)
            for i, Ai in enumerate(A):
                xa = tools.amplitude(A[i, :], config['A']['filter'], clock)
                xb = tools.amplitude(B[i, :], config['B']['filter'], clock)

                ta = tools.zero_crossing(A[i, :], config['A']['filter']['B'], 
                        falling=False)
                tb = tools.zero_crossing(B[i, :], config['B']['filter']['B'], 
                        falling=False)

                Ea = E(xa, config['A']['calib'])
                Eb = E(xb, config['B']['calib'])

                all_data.append([Ea, Eb, ta, tb])
                if (config['A']['window'][0] <= Ea <= config['A']['window'][1]
                        and
                    config['B']['window'][0] <= Eb <= config['B']['window'][1]):
                    good_data.append([Ea, Eb, ta, tb])
            tnow = datetime.datetime.now()
            dt = (tnow - t0).total_seconds()
            dt_plot = (tnow - t_plot).total_seconds()
            if dt_plot > t_update:
                update_plots(axes, lines_all, lines_good, all_data, good_data,
                        config['ch_range'], config['t_range'])
                time_text.set_text('t = {:.1f} s'.format(dt))
                time_text.set_x(axes[0][0].get_xlim()[0] + 1.0)
                time_text.set_y(axes[0][0].get_ylim()[1] * 0.9)
            if t_max > 0:
                if n_max < 0:
                    if args.verbose:
                        print('{:.2f} {:.1f} {:.1f} {:.3f} {:.3f}'.format(
                            dt, Ea, Eb, ta, tb))
                    else:
                        tools.progress_bar(dt, t_max, dt)
                if dt >= t_max:
                    break
            if n_max > 0:
                if args.verbose:
                    print(Ea, Eb, ta, tb)
                else:
                    tools.progress_bar(n, n_max, dt)
                if len(good_data) >= n_max:
                    break
        except KeyboardInterrupt:
            print('\r Stop                ')
            break

    footer = '* Stop at {}\n'.format(datetime.datetime.now())
    footer += '* Total running time: {:.3f} s\n'.format(dt)
    footer += '* Total events: {}\n'.format(len(all_data))
    footer += '* Total good events: {}\n'.format(len(good_data))

    print(footer)
    s.close()

    all_data = numpy.array(all_data)
    good_data = numpy.array(good_data)

    if len(all_data) == 0:
        print('No data collected')
        exit()

    if args.list is not None:
        out_file_name = '{0}_{1.year}{1.month:02}{1.day:02}_{1.hour:02}'\
                '{1.minute:02}{1.second:02}.txt'.format(args.list, t0)
        numpy.savetxt(out_file_name, all_data, fmt='%.3f', header=header,
                footer=footer, delimiter=' ')


    update_plots(axes, lines_all, lines_good, all_data, good_data,
            config['ch_range'], config['t_range'])

    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 3] - good_data[:, 2],
                bins=2 * config['t_range'],
                range=(-config['t_range'], config['t_range']))
        try:
            t0 = edges[numpy.argmax(bins)] 
            popt, pcon = curve_fit(gaussian, edges[:-1] + 0.5, bins, 
                                    p0 = [t0, 1.0, len(good_data)])
            xf = numpy.linspace(edges[0], edges[-1], 10000)
            axes[0][0].plot(xf, gaussian(xf, *popt), ls='--', color='orange')
            print('* dT:')
            print('      t0 = {0[0]:.2f}, s = {0[1]:.3f} A = {0[2]:.1f}'
                    .format(popt))
        except RuntimeError:
            print('* dT: could not fit selected data')
            pass

        bins, edges = numpy.histogram(good_data[:, 0], 
                range=(0, config['ch_range']), bins=config['ch_range'])
        x0 = edges[numpy.argmax(bins)] 
        xf = numpy.linspace(0, config['ch_range'], config['ch_range'] * 10)
        try:
            popt, pcon = curve_fit(gaussian, edges[:-1] + 0.5, bins, 
                                    p0 = [x0, x0 * 0.05, len(good_data)])
            axes[0][1].plot(edges[:-1], bins, ds='steps-mid', color='blue')
            axes[0][1].plot(xf, gaussian(xf, *popt), ls='--', color='violet')
            print('* CH A:')
            print('      x0 = {0[0]:.2f} s = {0[1]:.3f} A = {0[2]:.1f}'
                    .format(popt))
        except RuntimeError:
            print('* CH A: could not fit selected data')
            pass

        bins, edges = numpy.histogram(good_data[:, 1],
                range=(0, config['ch_range']), bins=config['ch_range'])
        try:
            x0 = edges[numpy.argmax(bins)] 
            popt, pcon = curve_fit(gaussian, edges[:-1] + 0.5, bins, 
                                    p0 = [x0, x0 * 0.05, len(good_data)])
            axes[1][0].plot(edges[:-1], bins, ds='steps-mid', color='red')
            axes[1][0].plot(xf, gaussian(xf, *popt), ls='--', color='orange')
            print('* CH B:')
            print('      x0 = {0[0]:.2f} s = {0[1]:.3f} A = {0[2]:.1f}'.
                    format(popt))
        except RuntimeError:
            print('* CH B: could not fit selected data')
            pass

    fig.canvas.draw()
    fig.canvas.flush_events()

    print('Press any key to exit')
    try:
        while True:
            key = fig.waitforbuttonpress(10)
            if key:
                break
    except KeyboardInterrupt:
        print('Done')
