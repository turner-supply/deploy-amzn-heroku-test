from flask import Flask, render_template, request
import pandas as pd
from pathlib import Path
from datetime import datetime
import createNB as nb
from pathlib import Path
import tkinter as tk 
from tkinter.filedialog import askopenfilename
from flask import send_file
from flaskwebgui import FlaskUI
    

app = Flask(__name__) 

ui = FlaskUI(app=app, server="flask", width=1100, height=750) 

place_dict = {'amznfile':'',
         'ordfile':''}

@app.route('/')
def root():
    return render_template('homePage.html', fill='')




@app.route('/data', methods = ['GET','POST'])
def data(): 
    global df
    global ordCost

    global sums_fba
    global sums_fbm
    global sf
    global description
    global graph

    try:
        if request.method == 'POST':

            #import Amazon sales report
            if request.form.get('action') == 'Select Amazon File':

            #pass selected files into create nb folder   
                root = tk.Tk()
                root.withdraw()
                amznfilename = askopenfilename()
                root.destroy()
                amznfile = amznfilename.split('/')[-1]
                place_dict.update(amznfile=amznfile)
                amznfile = place_dict['amznfile']
                ordfile = place_dict['ordfile']
    
                try:
                    if amznfilename.split('.')[-1] == 'xlsx':
                        df = pd.read_excel(amznfilename)
                    else:
                        df = pd.read_csv(amznfilename)

                    return render_template('homePage.html', amznfile=amznfile, ordfile_dict=ordfile)
                except Exception:
                    e = 'Please select .csv or .xlsx file'
                    return render_template('homePage.html', error_amzn=e)
                

                

            if request.form.get('action') == 'Select Cost File':
            #pass selected files into create nb folder   
                root = tk.Tk()
                root.withdraw()
                ordfilename = askopenfilename()
                root.destroy()

                print(ordfilename)
                ordfile = ordfilename.split('/')[-1]
                place_dict.update(ordfile=ordfile)
                amznfile = place_dict['amznfile']
                ordfile = place_dict['ordfile']

                try:
                    if ordfilename.split('.')[-1] == 'xlsx':
                        ordCost = pd.read_excel(ordfilename)
                    else:
                        ordCost = pd.read_csv(ordfilename)

                    return render_template('homePage.html', amznfile=amznfile,  ordfile=ordfile)

                except Exception:
                    e = 'Please select .csv or .xlsx file'
                    return render_template('homepage.html', error_cost=e)


            if request.form.get('action')=='Generate Report':
                try:
                    sums_fba, sums_fbm, sf, error = nb.main(df, ordCost)
                    if not error:
                        return render_template('foundPage.html',  tables=[sums_fbm.to_html()], titles=df.columns.values)
                    else:
                        e = 'Invalid document formatting - Please ensure proper data formatting'
                        return render_template('homePage.html',  error_gen=e)
                except Exception:
                    e = 'Invalid document formatting - Please ensure proper data formatting'
                    return render_template('homePage.html',  error_gen=e)
                    #return render_template('foundPage.html',  tables=[sums_fbm.to_html()], titles=df.columns.values)

            
            
            
            if request.form.get('action')=='Download':
                    

                date = datetime.today().strftime('%Y-%m-%d-%S')
                downloads_path = downloads_path = str(Path.home() / 'Downloads')                

                with pd.ExcelWriter(f'{downloads_path}\\AMZNReport{date}.xlsx', engine='xlsxwriter') as writer:
                    sums_fba.to_excel(writer, sheet_name='FBA')
                    sums_fbm.to_excel(writer, sheet_name='FBM')
                    sf.to_excel(writer, sheet_name='Additional')

                return '', 204
            

            if request.form.get('action')=='Download Template':
                path = 'template/AMZNAnalysisCostTemplate.csv'

                return send_file(path, as_attachment=True)


            
    except Exception as e:
        # e holds description of the error
        error_text = '<p>/data - The error:<br>' + str(e) + '- Please ensure proper formatting. Refresh page and try again </p>'
        hed = '<h1>Error</h1>'
        return hed + error_text


'''
need to format and create excel sheet
add download button
add use existing cost file
add importing of cost file in certain format (when sx is updated still able to be used)
                sku | cost
          ----------|-----
          073134801 | 30.32
add option to exclude cost of goods?

'''



if __name__ == '__main__':
    ui.run()