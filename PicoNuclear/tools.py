"""K. Miernik 2019
k.a.miernik@gmail.com
Distributed under GNU General Public Licence v3

Some useful functions that could be used with pico_pet script and
other setups.

"""
import datetime
import numpy
import xml.dom.minidom
from scipy.interpolate import CubicSpline


def progress_bar(n, n_max, time_to_n=None):
    """
    Show progress bar with arrow, completed percentage and optional
    current time and projected time to finish.
    """
    print('\r', end='')
    text = ''
    done = int(n / n_max * 40)
    text += ('[' + '=' * (done - 1) + '>' + '.' * (40 - done - 1) + ']' + 
            ' {:>5.2f}%  '.format((n / n_max) * 100))
    if time_to_n is not None:
        text += '{:>5.1f} s (est. {:>5.1f} s)     '.format(time_to_n, 
                time_to_n * n_max / n)
    print(text, end='', flush=True)


def get_number(text, default, number_type='float'):
    try:
        if number_type == 'float':
            r = float(text)
        else:
            r = int(text)
    except (AttributeError, ValueError):
        print('Warning, could not convert', text, 'to', number_type, 
               'reverting to default value')
        return default
    return r


def load_configuration(file_name):
    configuration = {}
    try:
        dom = xml.dom.minidom.parse(file_name)
        config = dom.getElementsByTagName('config')[0]

        hardware = config.getElementsByTagName('hardware')[0]

        samples = hardware.getElementsByTagName('samples')[0]
        configuration['timebase'] = get_number(
                samples.getAttribute('timebase'), 4, 'int')
        configuration['pre'] = get_number(
                samples.getAttribute('pre'), 100, 'int')
        configuration['post'] = get_number(
                samples.getAttribute('post'), 1000, 'int')
        configuration['captures'] = get_number(
                                    samples.getAttribute('captures'), 1, 'int')

        trigger = hardware.getElementsByTagName('trigger')[0]
        configuration['trigger'] = {
                'source' : trigger.getAttribute('source').upper(),
                'direction' : trigger.getAttribute('direction').upper(),
                'threshold' : get_number(trigger.getAttribute('threshold'), 
                                        0.0),
                'autotrigger': get_number(trigger.getAttribute('autotrigger'),
                                        0, 'int')
                }


        channels = hardware.getElementsByTagName('channel')
        for ch in channels:
            name = ch.getAttribute('name').upper()
            coupling = ch.getAttribute('coupling').upper()
            v_range = get_number(ch.getAttribute('range'), 1.0)
            offset = get_number(ch.getAttribute('offset'), 0.0)

            trapez = ch.getElementsByTagName('filter')[0]
            L = get_number(trapez.getAttribute('L'), 10, 'int')
            G = get_number(trapez.getAttribute('G'), 10, 'int')
            B = get_number(trapez.getAttribute('B'), 10, 'int')
            tau = get_number(trapez.getAttribute('tau'), 10)
            method = trapez.getAttribute('method')

            configuration[name] = { 
                                    'coupling' : coupling,
                                    'range' : v_range,
                                    'offset' : offset,
                                    'filter' : {'L' : L, 
                                                'G' : G, 
                                                'tau' : tau,
                                                'B' : B, 
                                                'method' : method
                                                }
                                }

        analysis = config.getElementsByTagName('analysis')[0]
        channels = analysis.getElementsByTagName('channel')
        for ch in channels:
            name = ch.getAttribute('name').upper()
            calib = ch.getAttribute('calibration')
            calib = calib.split(',')
            calib_params = []
            for par in calib:
                calib_params.append(float(par))

            window = ch.getAttribute('window')
            window = window.split(',')
            window_params = []
            for par in window:
                window_params.append(float(par))

            configuration[name]['calib'] = calib_params
            configuration[name]['window'] = window_params

    except (ValueError, IndexError) as err:
        print(err)
        return False
    return configuration


def trapezoidal(v, k, m, tau):
    N = len(v)
    d = numpy.zeros(N)
    p = numpy.zeros(N)
    r = numpy.zeros(N)
    s = numpy.zeros(N)
    l = k + m
    M = 1 / (numpy.exp(1 / tau) - 1)

    d[0] = v[0]
    p[0] = d[0]
    r[0] = p[0] + M * d[0]
    s[0] = r[0]

    for n in range(1, k):
        d[n] = v[n]
        p[n] = p[n-1] + d[n]
        r[n] = p[n] + M * d[n]
        s[n] = s[n-1] + r[n]

    for n in range(k, l):
        d[n] = v[n] - v[n-k]
        p[n] = p[n-1] + d[n]
        r[n] = p[n] + M * d[n]
        s[n] = s[n-1] + r[n]

    for n in range(l, l + k):
        d[n] = v[n] - v[n-k] - v[n-l]
        p[n] = p[n-1] + d[n]
        r[n] = p[n] + M * d[n]
        s[n] = s[n-1] + r[n]

    for n in range(l + k, N):
        d[n] = v[n] - v[n-k] - v[n-l] + v[n-l-k]
        p[n] = p[n-1] + d[n]
        r[n] = p[n] + M * d[n]
        s[n] = s[n-1] + r[n]

    return max(abs(s)) / k, s


def zero_crossing(trace, base=15, shift=10, chi=0.6, falling=True):
    """
    NIMA 775 (2015) 71–76
    """

    try:
        bs = numpy.average(trace[0:base])
        inv = numpy.zeros(trace.shape)
        inv[shift:] = trace[0:-shift] - bs
        zc = chi * (trace - bs) - inv
        if falling:
            zc *= -1
        t_lim, = numpy.unravel_index(zc.argmax(), zc.shape)
        t0 = numpy.argmax(zc[t_lim:] < 0) + t_lim

        t_zc = numpy.arange(t0 - 3, t0 + 3)
        y_zc = zc[t0-3:t0+3]
        cs = CubicSpline(t_zc, y_zc)
        r = cs.solve(0.0)

        for ri in r:
            if numpy.isreal(ri) and t_zc[0] < ri < t_zc[-1]:
                return ri
    except ValueError:
        pass
    return 0



def amplitude(s, params, method='trapezoidal'):
    if params['method'] == 'trapezoidal':
        A, sa = trapezoidal(s, params['L'], params['G'], params['tau'])
    else:
        baseline = s[0:params['B']].sum() / params['B']
        if params['method'] == 'sum':
            A = abs((s - baseline).sum()) / s.shape[0]
        else:
            A = max(abs(s - baseline))
    return A
