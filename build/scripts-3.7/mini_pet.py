import argparse
import numpy
import matplotlib.pyplot as plt
import Picopet.tools as tools
from Picopet.pico3000a import PicoScope3000A
from scipy.optimize import curve_fit


def E(x, calib):
    r = 0
    for i, c in enumerate(calib):
        r += c * x**i
    return r


def gaussian(x, x0, s, A): 
    return (A / numpy.sqrt(2 * numpy.pi * s**2) * 
            numpy.exp(-(x-x0)**2 / (2 * s**2)))



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

    config = tools.load_configuration(args.config)

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
                  threshold=config['trigger']['threshold'] + 
                  config[config['trigger']['source']]['offset'],
                  direction=config['trigger']['direction'], 
                  auto_trigger=config['trigger']['autotrigger'])

    t0 = datetime.datetime.now()
    dt = (datetime.datetime.now() - t0).total_seconds()

    header += 'Start at {}\n'.format(t0)
    print('* Start at', t0)

    all_data = []
    good_data = []
    while True:
        try:
            t, [A, B] = s.measure(config['pre'], config['post'],
                                  num_captures=config['captures'],
                                  timebase=config['timebase'])
            for i, Ai in enumerate(A):
                xa = tools.amplitude(A[i, :], config['A']['filter'], 'trapezoidal')
                xb = tools.amplitude(B[i, :], config['B']['filter'], 'trapezoidal')

                ta = tools.zero_crossing(A[i, :], config['A']['filter']['B'])
                tb = tools.zero_crossing(B[i, :], config['B']['filter']['B'])

                Ea = E(xa, config['A']['calib'])
                Eb = E(xb, config['B']['calib'])

                all_data.append([Ea, Eb, ta, tb])
                if (config['A']['window'][0] <= Ea <= config['A']['window'][1]
                        and
                    config['B']['window'][0] <= Eb <= config['B']['window'][1]):
                    good_data.append([Ea, Eb, ta, tb])
            dt = (datetime.datetime.now() - t0).total_seconds()
            if t_max > 0:
                if n_max < 0:
                    if args.verbose:
                        print('{:.2f} {:.1f} {:.1f} {:.3f} {:.3f}'.format(
                            dt, Ea, Eb, ta, tb))
                    else:
                        progress_bar(dt, t_max, dt)
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

    fig, axes = plt.subplots(2, 2)

    bins, edges = numpy.histogram(all_data[:, 3] - all_data[:, 2], bins=1000)
    axes[0][0].plot(edges[:-1], bins, ds='steps-mid', color='black')
    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 3] - good_data[:, 2],
                bins=1000)
        axes[0][0].plot(edges[:-1], bins, ds='steps-mid', color='red')
    #fig.delaxes(axes[0][0])

    max_A = max(all_data[:, 0])
    max_B = max(all_data[:, 1])
    ch_range = [0, int(max(max_A, max_B)) + 1]
    n_bins = 8192 if ch_range[1] > 8192 else ch_range[1]

    axes[1][1].plot(all_data[:, 0], all_data[:, 1], 's', 
            mfc='None', color='Black')
    if len(good_data > 0):
        axes[1][1].plot(good_data[:, 0], good_data[:, 1], 'o', 
                mfc='None', color='Red')
    axes[1][1].set_xlabel('Ch A')
    axes[1][1].set_ylabel('Ch B')
    axes[1][1].set_xlim(0, ch_range[1])
    axes[1][1].set_ylim(0, ch_range[1])

    bins, edges = numpy.histogram(all_data[:, 0], range=ch_range, 
            bins=n_bins)
    axes[0][1].plot(edges[:-1], bins, ds='steps-mid', color='black')
    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 0], range=ch_range, 
                        bins=n_bins)
        x0 = edges[numpy.argmax(bins)] 
        popt, pcon = curve_fit(gaussian, edges[:-1] + 0.5, bins, 
                                p0 = [x0, x0 * 0.05, len(good_data)])
        xf = numpy.linspace(ch_range[0], ch_range[1], 
                            (ch_range[1] - ch_range[0]) * 10)
        axes[0][1].plot(edges[:-1], bins, ds='steps-mid', color='blue')
        axes[0][1].plot(xf, gaussian(xf, *popt), ls='--', color='violet')
        print('* CH A:')
        print('      x0 = {0[0]:.2f} s = {0[1]:.3f} A = {0[2]:.1f}'
                .format(popt))
    axes[0][1].set_xlabel('Ch A')

    bins, edges = numpy.histogram(all_data[:, 1], range=ch_range, 
                        bins=n_bins)
    axes[1][0].plot(edges[:-1], bins, ds='steps-mid', color='black')
    if len(good_data > 0):
        bins, edges = numpy.histogram(good_data[:, 1], range=ch_range, 
                        bins=n_bins)
        x0 = edges[numpy.argmax(bins)] 
        popt, pcon = curve_fit(gaussian, edges[:-1] + 0.5, bins, 
                                p0 = [x0, x0 * 0.05, len(good_data)])
        axes[1][0].plot(edges[:-1], bins, ds='steps-mid', color='red')
        axes[1][0].plot(xf, gaussian(xf, *popt), ls='--', color='orange')
        print('* CH B:')
        print('      x0 = {0[0]:.2f} s = {0[1]:.3f} A = {0[2]:.1f}'.
                format(popt))
    axes[1][0].set_xlabel('Ch B')

    fig.set_size_inches(9, 9)
    fig.tight_layout()
    plt.show()

