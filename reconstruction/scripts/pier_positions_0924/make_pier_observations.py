import json,math,sys
request=json.load(open(sys.argv[1]));targets=[]
for rec in request['targets']:
 views=[]
 for key,h,x in rec.pop('pixels'):
  v=dict(request['panos'][key]);v.update(view_heading=h,target_pixel_x=x,image_width=1280,image_height=720,assumed_focal_px=360,heading=(h+math.degrees(math.atan2(x-640,360)))%360);views.append(v)
 rec['views']=views;targets.append(rec)
json.dump({'targets':targets},open(sys.argv[2],'w'),indent=2)
