import flask
import io
import os
import shutil
import matplotlib.colors as mcolors
from flask import Flask
from flask import request
from flask import make_response
from gevent import pywsgi
from PIL import Image
from wsgiref.simple_server import make_server


from filter import ColorFilter
from clr_class import ColorInfo


global_count = 0

app = Flask(__name__,template_folder='templates')

UPLOAD_FOLDER = 'static/upload/'
UPLOAD_FOLDER_response = os.path.join(app.template_folder,'response.html')

def read_file(file_name):
	with open(file_name, encoding='UTF-8') as f:
		read_all = f.read()
		f.close()

	return read_all

def rewrite_file(file_name, data):
	with open(file_name, 'w', encoding='UTF-8') as f:
		f.write(data)
		f.close()

def replace(file_name, replace_infos, rgbcolor):
	content = read_file(file_name)
	color1 = replace_infos.get("COLOR_1")
	color2 = replace_infos.get("COLOR_2")
	color3 = replace_infos.get("COLOR_3")
	color4 = replace_infos.get("COLOR_4")
	color5 = replace_infos.get("COLOR_5")
	color6 = replace_infos.get("COLOR_6")
	filtered_file_url = replace_infos.get('URL_FILTERED')

	content = content.replace("HUIYANJIAN_COLOR_1", str(color1))
	content = content.replace("HUIYANJIAN_COLOR_2", str(color2))
	content = content.replace("HUIYANJIAN_COLOR_3", str(color3))
	content = content.replace("HUIYANJIAN_COLOR_4", str(color4))
	content = content.replace("HUIYANJIAN_COLOR_5", str(color5))
	content = content.replace("HUIYANJIAN_COLOR_6", str(color6))
	content = content.replace("YOUR_COLOR_AVG", rgbcolor)
	content = content.replace("URL_FILTERED", filtered_file_url)
	rewrite_file(file_name, content)

def response_html_create(color_des, filtered_filepath, rgbcolor):
	base_name_html = os.path.basename(filtered_filepath)
	base_name_html = base_name_html.split('.')[0]
	base_name_html = base_name_html + ".html"
	full_name_html = os.path.join(app.template_folder, base_name_html)
	shutil.copy(UPLOAD_FOLDER_response, full_name_html)
	full_name_html_url = "http://api.x-hpc.top:1234/"+UPLOAD_FOLDER+os.path.basename(filtered_filepath)
	print(filtered_filepath)
	print(filtered_filepath)
	print(full_name_html_url)
	print(full_name_html_url)
	replace_info = {
				"COLOR_1":color_des.get("color1"),
				"COLOR_2":color_des.get("color2"),
				"COLOR_3":color_des.get("color3"),
				"COLOR_4":color_des.get("color4"),
				"COLOR_5":color_des.get("color5"),
				"COLOR_6":color_des.get("color6"),
				"URL_FILTERED":full_name_html_url }
	replace(full_name_html, replace_info, rgbcolor)
	return os.path.basename(full_name_html)

def call_color_filter(color, input_file_path):
	_filter = ColorFilter(color, input_file_path)
	_filter.do_filter()
	return _filter._output_file_path


@app.route("/")
def root():
	return "TEST....."

@app.route('/up_photo', methods=['post'])
def up_photo():
	global global_count
	global_count = global_count + 1
	img = request.files.get('photo')
	photo_info = request.form.to_dict()
	color = photo_info.get('color')
	file_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)
	origin_file_name = img.filename.split('.')[0]
	origin_file_name = "_" + str(global_count) + "_" + origin_file_name
	origin_file_suff = img.filename.split('.')[1]
	origin_file_name = origin_file_name + "." + origin_file_suff
	file_path = os.path.join(file_dir, origin_file_name)
	img.save(file_path)

	_filter = ColorFilter(color, file_path)
	filtered_file_path = _filter.do_filter() 
	color_info = ColorInfo(filtered_file_path)
	color_des = color_info.compute_color();
	rgb_color = (color_info._r, color_info._g, color_info._b)
	rgb_color = mcolors.to_hex(rgb_color)
	filtered_file_path = _filter.do_crop_out(color_info._minx, color_info._miny, color_info._maxx, color_info._maxy) 
	print(filtered_file_path)
	print(filtered_file_path)
	result_html_file_path = response_html_create(color_des, filtered_file_path, rgb_color)
	print(result_html_file_path)
	return flask.render_template(result_html_file_path)

@app.route('/upload')
def upload_test():
		return flask.render_template('new.html')

if __name__ == "__main__":
	server1 = make_server('0.0.0.0', 1234, app)
	server1.serve_forever()
	#server2 = make_server('0.0.0.0', 8010, app)
	#server2.serve_forever()
	server3 = make_server('0.0.0.0', 9991, app)
	server3.serve_forever()
