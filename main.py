import PySimpleGUI as sg
import scrapper as c
import re
import pandas as pd

header_list = ['Market', 'Price', 'Quantity', 'Shipping methods']
header_widths = [23, 7, 7, 15]
df_source = {'Market': [],
             'Price': [],
             'Quantity': [],
             'Shipping methods': []}
df = pd.DataFrame(df_source)

sg.theme('DefaultNoMoreNagging')
layout = [[sg.Text('Select option to start', text_color='green', size=(45, 1), font=('Helvetica', 12, 'bold'),
                   key='MSG')],
          [sg.Text('Product id:', size=(10, 1)), sg.InputText(size=(30, 1), pad=(15, 0), key='PRODUCT'),
           sg.Combo([(1, 'Casto'), (2, 'Leroy'), (3, 'OBI')], key='OPTION', enable_events=True)],
          [sg.Button('Check', size=(10, 1), key='CHECK', disabled=True),
           sg.ProgressBar(100, orientation='h', size=(20, 20), key='PROGRESS',
                          bar_color=('#082567', '#f0f0f0'))],
          [sg.Table(values=df.values.tolist(),
                    headings=header_list,
                    key='GRID',
                    display_row_numbers=True,
                    auto_size_columns=False,
                    num_rows=25,
                    col_widths=header_widths)]]

window = sg.Window('Price Checker', layout)


def validate_input():
    if re.search("^[0-9]+$", values['PRODUCT']) is None:
        window['MSG'].update('Product id must be a valid number', text_color='red')
        return False
    else:
        window['CHECK'].update(disabled=True)
        window['OPTION'].update(disabled=True)
        window['PRODUCT'].update(disabled=True)
        window['MSG'].update('Checking product data...', text_color='green')
        return True


while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break

    if event == 'OPTION':
        markets_map = c.get_markets(values['OPTION'][0])
        if len(markets_map) == 0:
            window['MSG'].update('Failed to init market\'s list', text_color='red')
        else:
            window['MSG'].update('Market\'s list init completed, enter product id', text_color='green')
            window['CHECK'].update(disabled=False)
            window['PROGRESS'].update(current_count=0, max=len(markets_map))

    if event == 'CHECK':
        if validate_input():
            df_source = {'Market': [],
                         'Price': [],
                         'Quantity': [],
                         'Shipping methods': []}
            counter = 0
            try:
                for m in markets_map.keys():
                    counter = counter + 1
                    element = c.get_product_details(str(values['PRODUCT']), m, int(values['OPTION'][0]))
                    window['PROGRESS'].update_bar(counter)
                    df_source['Market'].append(markets_map[m])
                    df_source['Price'].append(element['price'])
                    df_source['Quantity'].append(element['qty'])
                    df_source['Shipping methods'].append(element['shippingMethods'])

                df = pd.DataFrame(df_source)
                df.sort_values(by='Price', ignore_index=True, inplace=True)
                window['MSG'].update('Check is done, enter next id', text_color='green')
            except (TypeError, KeyError):
                window['MSG'].update('Something went wrong, check product id', text_color='red')
            finally:
                window['GRID'].update(df.values.tolist())
                window['CHECK'].update(disabled=False)
                window['OPTION'].update(disabled=False)
                window['PRODUCT'].update(disabled=False)

window.close()
