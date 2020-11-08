import PySimpleGUI as sg
import casto as c
import re
import pandas as pd

markets_map = c.get_markets()
header_list = ['Market', 'Price', 'Quantity', 'Shipping methods']
header_widths = [23, 7, 7, 15]
df_source = {'Market': [],
             'Price': [],
             'Quantity': [],
             'Shipping methods': []}
df = pd.DataFrame(df_source)
init_msg = 'Init completed. Enter product id' if len(markets_map) > 0 else 'Failed to init market\'s list'
init_msg_color = 'green' if len(markets_map) > 0 else 'red'

sg.theme('DefaultNoMoreNagging')
layout = [[sg.Text(init_msg, text_color=init_msg_color, size=(30, 1), font=('Helvetica', 12, 'bold'),
                   key='MSG')],
          [sg.Text('Product id:', size=(10, 1)), sg.InputText(size=(30, 1), pad=(15, 0))],
          [sg.Button('Check', size=(10, 1), key='CHECK', disabled=len(markets_map) == 0),
           sg.ProgressBar(len(markets_map), orientation='h', size=(20, 20), key='PROGRESS',
                          bar_color=('#082567', '#f0f0f0'))],
          [sg.Table(values=df.values.tolist(),
                    headings=header_list,
                    key='GRID',
                    display_row_numbers=True,
                    auto_size_columns=False,
                    num_rows=25,
                    col_widths=header_widths)]]

window = sg.Window('Casto Price Checker', layout)


def validate_input():
    if re.search("^[0-9]+$", values[0]) is None:
        window['MSG'].update('Product id must be a valid number', text_color='red')
        return False
    else:
        window['CHECK'].update(disabled=True)
        window['MSG'].update('Checking product data...', text_color='green')
        return True


while True:
    event, values = window.read(timeout=10)
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break

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
                    data = c.get_product_details(str(values[0]), m)
                    window['PROGRESS'].update_bar(counter)
                    df_source['Market'].append(markets_map[m])
                    df_source['Price'].append(float(data['products'][str(values[0])]['price']))
                    df_source['Quantity'].append(data['products'][str(values[0])]['qty'])
                    df_source['Shipping methods'].append(
                        [e[0] for e in data['products'][str(values[0])]['shippingMethods'].items() if e[1] is True])

                df = pd.DataFrame(df_source)
                df.sort_values(by='Price', ignore_index=True, inplace=True)
                window['MSG'].update('Check is done, enter next id', text_color='green')
            except TypeError:
                window['MSG'].update('Something went wrong, check product id', text_color='red')
            finally:
                window['GRID'].update(df.values.tolist())
                window['CHECK'].update(disabled=False)

window.close()
