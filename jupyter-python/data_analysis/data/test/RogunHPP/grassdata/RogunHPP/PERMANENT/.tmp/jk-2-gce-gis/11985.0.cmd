d.rast -n map="topog_relief_color" bgcolor="white"
d.legend raster="topog_rast_resamp" lines=0 thin=1 labelnum=5 color="black" fontsize=48
d.grid size="2000" origin=0,0 direction="both" color="gray" border_color="black" text_color="gray" fontsize=20
d.vect map="topog_vect" layer="1" display="shape" type="point,line,boundary,area,face" color="green" fill_color="200:200:200" width=0 width_scale=1 icon="basic/x" size=5 label_layer="1" label_color="red" label_bgcolor="none" label_bcolor="none" label_size=8 xref="left" yref="center"
d.grid size="2000" origin=0,0 direction="both" color="gray" border_color="black" text_color="gray" fontsize=20
d.vect map="topog_vect" layer="1" display="shape" type="point,line,boundary,area,face" color="green" fill_color="200:200:200" width=0 width_scale=1 icon="basic/x" size=5 label_layer="1" label_color="red" label_bgcolor="none" label_bcolor="none" label_size=8 xref="left" yref="center"
d.grid size="2000" origin=0,0 direction="both" color="gray" border_color="black" text_color="gray" fontsize=20
