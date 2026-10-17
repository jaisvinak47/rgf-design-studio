import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="RGF Design Studio", page_icon="💧", layout="wide", initial_sidebar_state="expanded")
st.markdown('''<style>
:root { --navy:#10263d; --teal:#0f766e; --teal-light:#dff4ef; --ink:#182b45; --muted:#64748b; --line:#dce5ef; --canvas:#f4f7fb; }
.stApp { background:linear-gradient(180deg,#eef4f9 0%,#f7f9fc 280px,#f7f9fc 100%); color:var(--ink); }
.main .block-container { max-width:1450px; padding-top:1.6rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#10263d 0%,#173852 100%); }
[data-testid="stSidebar"] * { color:#f8fafc; }
[data-testid="stSidebar"] label { color:#e2edf6 !important; font-weight:600; }
[data-testid="stSidebar"] input { background:#f8fafc !important; color:#10263d !important; border-radius:10px !important; }
.hero { background:linear-gradient(120deg,#10263d 0%,#174a60 62%,#0f766e 100%); border-radius:22px; padding:30px 34px; color:#fff; margin-bottom:22px; box-shadow:0 12px 28px rgba(16,38,61,.14); }
.hero h1 { color:#fff !important; font-size:2.25rem; margin:0 0 8px 0; letter-spacing:-.7px; }
.hero p { color:#d9e8f1 !important; font-size:1.02rem; margin:0; }
.eyebrow { text-transform:uppercase; letter-spacing:2px; font-size:.72rem; font-weight:800; color:#a7f3d0; margin-bottom:9px; }
.section-note { color:#64748b; margin-top:-8px; margin-bottom:16px; }
h1,h2,h3,h4 { color:var(--ink); letter-spacing:-.35px; }
h2 { font-size:1.65rem !important; padding-top:12px; margin-top:1.6rem !important; border-bottom:1px solid var(--line); padding-bottom:10px; }
h3 { font-size:1.15rem !important; }
p, label { color:var(--ink); }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:16px; padding:17px 18px; box-shadow:0 3px 12px rgba(16,38,61,.045); }
[data-testid="stMetricLabel"] { color:#64748b !important; font-weight:650; }
[data-testid="stMetricValue"] { color:#10263d !important; font-weight:750; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input { border-radius:10px; }
.stButton button, .stDownloadButton button { border-radius:10px; font-weight:700; border:1px solid #0f766e; }
.stDownloadButton button { background:#0f766e; color:#fff; }
.stDownloadButton button:hover { background:#115e59; color:#fff; border-color:#115e59; }
.stAlert { border-radius:13px; }
div[data-testid="stVerticalBlock"] > div:has(> div > .section-card) { background:white; }
.small-muted { color:#64748b; font-size:.88rem; }
hr { border-color:var(--line); }
@media (max-width: 800px) { .hero { padding:22px; } .hero h1 { font-size:1.7rem; } }
</style>''', unsafe_allow_html=True)
st.markdown('''<div class="hero"><div class="eyebrow">Water Treatment • Design Workspace</div><h1>💧 Rapid Gravity Filter Design Studio</h1><p>Guided calculations for filter sizing, media resistance, piping losses and hydraulic head summary.</p></div>''', unsafe_allow_html=True)
st.caption("Chapter 10 • Design Example 10.13 • Editable inputs and calculation tables")
st.warning("Preliminary engineering calculator. The worked-example hydraulic profile is reproduced separately from diagnostic clean-media calculations. Verify equations, assumptions, coefficients, and reference values before design use.")
st.sidebar.markdown("## 💧 RGF Studio")
st.sidebar.caption("DESIGN BASIS · EDIT INPUTS BELOW")
st.sidebar.header('Design basis')
project=st.sidebar.text_input('Project name','Qasim Example 10.13')
flow_mld=st.sidebar.number_input('Plant flow (MLD)',min_value=0.01,value=113.5,step=1.0)
filters=st.sidebar.number_input('Total filters',min_value=1,value=8,step=1)
oos=st.sidebar.number_input('Filters out of service',min_value=0,value=1,step=1)
rate=st.sidebar.number_input('Filtration rate (m³/m²·h)',min_value=0.1,value=10.0,step=0.5)
terminal=st.sidebar.number_input('Terminal head loss (m)',min_value=0.0,value=2.5,step=0.1)
operating=int(filters-oos)
if operating<1: st.error('At least one filter must be operating.'); st.stop()
Qday=flow_mld*1000; Qhour=Qday/24; Qsec=Qday/86400; qf=Qsec/operating
A_total=Qhour/rate; A_filter=A_total/operating

st.info('**How to use:** Start with the design basis in the left panel, then work down each numbered section. Tables are editable; totals update automatically. Use the final summary to export the current calculation results.', icon='🧭')

st.header('01  ·  Filter sizing')
st.caption('Establish the design flow, operating filters and required filter area.')
c=st.columns(4)
c[0].metric('Plant flow',f'{flow_mld:.2f} MLD'); c[1].metric('Operating filters',str(operating)); c[2].metric('Flow/filter',f'{qf:.5f} m³/s'); c[3].metric('Area/filter',f'{A_filter:.2f} m²')
x,y=st.columns(2)
with x: Lf=st.number_input('Provided filter length (m)',min_value=0.1,value=8.25,step=0.25)
with y: Wf=st.number_input('Provided filter width (m)',min_value=0.1,value=8.25,step=0.25)
st.metric('Provided area per filter',f'{Lf*Wf:.2f} m²')

st.header('02  ·  Effective size of anthracite')
st.caption('Estimate the anthracite size using the settling relationship selected from your reference.')
st.write('Equal-settling relationship: use the exact relationship and exponent specified in your reference. This calculator provides an editable power-law form for checking, not a substitute for the source equation.')
a,b,c=st.columns(3)
with a: d_sand=st.number_input('Sand effective size dₛ (mm)',min_value=0.01,value=0.50,step=0.05)
with b: sg_sand=st.number_input('Sand specific gravity',min_value=0.1,value=2.65,step=0.05)
with c: sg_anth=st.number_input('Anthracite specific gravity',min_value=0.1,value=1.55,step=0.05)
exp=st.number_input('Settling relationship exponent (verify reference)',min_value=0.01,value=0.5,step=0.05,help='Set this to the exponent in the exact equation from your reference.')
if sg_anth>1 and sg_sand>1:
    d_anth=d_sand*((sg_sand-1)/(sg_anth-1))**exp
    st.metric('Calculated anthracite effective size (provisional)',f'{d_anth:.3f} mm')
else: d_anth=d_sand; st.error('Specific gravities must be greater than 1 for this form.')

st.header('03  ·  Clean filter media head loss')
st.caption('Calculate the anthracite and sand contributions separately, then combine them once.')
st.write('Uses Reynolds number and a friction-factor form. Confirm the exact equation/constants and unit convention against Chapter 10 before relying on results.')
a,b=st.columns(2)
with a:
 st.subheader('Anthracite')
 da=st.number_input('Anthracite size (mm)',min_value=0.01,value=float(d_anth),step=0.05,key='da')
 ha=st.number_input('Anthracite depth (m)',min_value=0.01,value=0.50,step=0.05)
 ea=st.number_input('Anthracite porosity',min_value=0.01,max_value=0.99,value=0.48,step=0.01)
with b:
 st.subheader('Sand')
 ds=st.number_input('Sand size (mm)',min_value=0.01,value=0.50,step=0.05,key='ds')
 hs=st.number_input('Sand depth (m)',min_value=0.01,value=0.25,step=0.05)
 es=st.number_input('Sand porosity',min_value=0.01,max_value=0.99,value=0.40,step=0.01)
mu=1.002e-3; rho=998.2; g=9.81; vf=rate/3600
# Source-style preliminary relation: Re=rho*v*d/mu; f=150(1-e)/Re+1.75; h=f*(L/d)*(v^2/(2*g))*((1-e)/e^3) [verify exact textbook form]
def media_calc(dmm,depth,por):
 d=dmm/1000
 Re=rho*vf*d/mu if d>0 else 0
 f=150*(1-por)/Re+1.75 if Re>0 else 0
 h=f*(depth/d)*(vf**2/(2*g))*((1-por)/(por**3)) if d>0 and por>0 else 0
 return Re,f,h
Rea,fa,ha_loss=media_calc(da,ha,ea); Res,fs,hs_loss=media_calc(ds,hs,es)
media_total=ha_loss+hs_loss
st.dataframe(pd.DataFrame([{'Layer':'Anthracite','Reynolds number':Rea,'Friction factor':fa,'Head loss (m)':ha_loss},{'Layer':'Sand','Reynolds number':Res,'Friction factor':fs,'Head loss (m)':hs_loss},{'Layer':'TOTAL MEDIA','Reynolds number':None,'Friction factor':None,'Head loss (m)':media_total}]),width='stretch',hide_index=True)
st.metric('Combined clean-media head loss',f'{media_total:.4f} m')

st.header('04  ·  Influent piping — major friction loss')
st.caption('Set the number of pipe segments, then enter the flow, diameter, length and friction coefficient for each.')
st.write('Enter the number of pipe segments first, then edit each segment. Hazen–Williams SI equation is used here.')
default_seg=pd.DataFrame([{'Segment':'I','Flow (m³/s)':0.657,'Diameter (m)':0.91,'Length (m)':5.725,'HW C':120},{'Segment':'II','Flow (m³/s)':0.469,'Diameter (m)':0.91,'Length (m)':8.55,'HW C':120},{'Segment':'III','Flow (m³/s)':0.094,'Diameter (m)':0.91,'Length (m)':39.85,'HW C':120},{'Segment':'IV','Flow (m³/s)':0.188,'Diameter (m)':0.45,'Length (m)':4.8,'HW C':120}])
nseg=st.number_input('Number of influent pipe segments',min_value=1,max_value=30,value=4,step=1)
seg_init=default_seg.head(int(nseg)).copy()
while len(seg_init)<int(nseg): seg_init.loc[len(seg_init)]={'Segment':f'S{len(seg_init)+1}','Flow (m³/s)':qf,'Diameter (m)':0.45,'Length (m)':1.0,'HW C':120}
segments=st.data_editor(seg_init,key='influent_segments',num_rows='fixed',width='stretch',hide_index=True)
def velocity(q,d): return 4*q/(math.pi*d*d) if q>=0 and d>0 else 0
def hw(L,q,d,C): return 10.67*L*q**1.852/(C**1.852*d**4.87) if L>0 and q>0 and d>0 and C>0 else 0
major_rows=[]
for _,r in segments.iterrows():
 q=float(r['Flow (m³/s)']); d=float(r['Diameter (m)']); L=float(r['Length (m)']); C=float(r['HW C'])
 major_rows.append({'Segment':r['Segment'],'Velocity (m/s)':velocity(q,d),'Major loss (m)':hw(L,q,d,C)})
major_df=pd.DataFrame(major_rows); major_in=float(major_df['Major loss (m)'].sum())
st.dataframe(major_df,width='stretch',hide_index=True); st.metric('Influent major-loss subtotal',f'{major_in:.4f} m')

st.header('05  ·  Influent piping — minor losses')
st.caption('Enter one row per fitting type and flow condition. Quantity is applied to the loss per fitting.')
st.write('Add one row per fitting type/size/flow condition. Quantity multiplies the loss of one fitting.')
fit_default=pd.DataFrame([{'Fitting type':'Isolation valve — Segment I','Quantity':1,'Flow (m³/s)':0.657,'Diameter (m)':0.91,'K':1.0},{'Fitting type':'Cross run-to-run — Segment I','Quantity':1,'Flow (m³/s)':0.657,'Diameter (m)':0.91,'K':0.60},{'Fitting type':'Cross run-to-run — Segment II','Quantity':1,'Flow (m³/s)':0.469,'Diameter (m)':0.91,'K':0.60},{'Fitting type':'Isolation valve — Segment III','Quantity':1,'Flow (m³/s)':0.094,'Diameter (m)':0.91,'K':1.0},{'Fitting type':'Cross run-to-branch','Quantity':1,'Flow (m³/s)':0.188,'Diameter (m)':0.45,'K':1.8},{'Fitting type':'Butterfly valve','Quantity':1,'Flow (m³/s)':0.188,'Diameter (m)':0.45,'K':1.2},{'Fitting type':'Outlet loss','Quantity':1,'Flow (m³/s)':0.188,'Diameter (m)':0.45,'K':1.0}])
nfit=st.number_input('Number of influent fitting rows',min_value=1,max_value=50,value=7,step=1)
fit_init=fit_default.head(int(nfit)).copy()
while len(fit_init)<int(nfit): fit_init.loc[len(fit_init)]={'Fitting type':'Fitting','Quantity':1,'Flow (m³/s)':qf,'Diameter (m)':0.45,'K':1.0}
fittings=st.data_editor(fit_init,key='influent_fittings',num_rows='fixed',width='stretch',hide_index=True)
def minor_table(df):
 rows=[]
 for _,r in df.iterrows():
  q=float(r['Flow (m³/s)']); d=float(r['Diameter (m)']); K=float(r['K']); qty=int(r['Quantity']); v=velocity(q,d); one=K*v*v/(2*g); rows.append({'Fitting':r['Fitting type'],'Quantity':qty,'Velocity (m/s)':v,'K':K,'Loss each (m)':one,'Total loss (m)':qty*one})
 return pd.DataFrame(rows)
minor_in_df=minor_table(fittings); minor_in=float(minor_in_df['Total loss (m)'].sum()); influent_total=major_in+minor_in
st.dataframe(minor_in_df,width='stretch',hide_index=True); st.metric('Influent minor-loss subtotal',f'{minor_in:.4f} m'); st.metric('TOTAL INFLUENT PIPING LOSS',f'{influent_total:.4f} m')

st.header('06  ·  Effluent piping')
st.caption('Calculate major friction losses and fitting losses for the effluent route.')
n_eff=st.number_input('Number of effluent pipe segments',min_value=1,max_value=30,value=1,step=1)
eff_seg_default=pd.DataFrame([{'Segment':'Effluent I','Flow (m³/s)':qf,'Diameter (m)':0.45,'Length (m)':5.0,'HW C':120}])
eff_init=eff_seg_default.copy()
while len(eff_init)<int(n_eff): eff_init.loc[len(eff_init)]={'Segment':f'E{len(eff_init)+1}','Flow (m³/s)':qf,'Diameter (m)':0.45,'Length (m)':1.0,'HW C':120}
effseg=st.data_editor(eff_init,key='effluent_segments',num_rows='fixed',width='stretch',hide_index=True)
eff_major_rows=[]
for _,r in effseg.iterrows():
 q=float(r['Flow (m³/s)']); d=float(r['Diameter (m)']); L=float(r['Length (m)']); C=float(r['HW C']); eff_major_rows.append({'Segment':r['Segment'],'Velocity (m/s)':velocity(q,d),'Major loss (m)':hw(L,q,d,C)})
eff_major_df=pd.DataFrame(eff_major_rows); eff_major=float(eff_major_df['Major loss (m)'].sum()); st.dataframe(eff_major_df,width='stretch',hide_index=True); st.metric('Effluent major loss',f'{eff_major:.4f} m')
n_eff_fit=st.number_input('Number of effluent fitting rows',min_value=1,max_value=50,value=1,step=1)
eff_fit_default=pd.DataFrame([{'Fitting type':'Bend / valve (edit)','Quantity':1,'Flow (m³/s)':qf,'Diameter (m)':0.45,'K':1.0}])
eff_fit_init=eff_fit_default.copy()
while len(eff_fit_init)<int(n_eff_fit): eff_fit_init.loc[len(eff_fit_init)]={'Fitting type':'Fitting','Quantity':1,'Flow (m³/s)':qf,'Diameter (m)':0.45,'K':1.0}
eff_fits=st.data_editor(eff_fit_init,key='effluent_fittings',num_rows='fixed',width='stretch',hide_index=True)
eff_minor_df=minor_table(eff_fits); eff_minor=float(eff_minor_df['Total loss (m)'].sum()); eff_total=eff_major+eff_minor
st.dataframe(eff_minor_df,width='stretch',hide_index=True); st.metric('Effluent minor loss',f'{eff_minor:.4f} m'); st.metric('Calculated effluent piping loss',f'{eff_total:.4f} m')
eff_profile=st.number_input('Effluent piping loss used in final reference profile (m)',min_value=0.0,value=0.05,step=0.01,help='Numerical 10.13 hydraulic profile uses 0.05 m. Change this to the calculated value if you are designing a different layout.')

st.header('07  ·  Gravel support and underdrain')
st.caption('Gravel layer losses are entered from the worked example because the exact source equation is not encoded here. Underdrain loss can use the source value or an orifice estimate.')
gravel_default=pd.DataFrame([{'Layer':'3.0 mm gravel','Depth (m)':0.05,'Porosity':0.45,'Reference loss (m)':0.0019},{'Layer':'4.5 mm gravel','Depth (m)':0.05,'Porosity':0.45,'Reference loss (m)':0.0006},{'Layer':'9.5 mm gravel','Depth (m)':0.075,'Porosity':0.50,'Reference loss (m)':0.0002},{'Layer':'15.5 mm gravel','Depth (m)':0.075,'Porosity':0.50,'Reference loss (m)':0.0001}])
gravel=st.data_editor(gravel_default,key='gravel_layers',num_rows='fixed',width='stretch',hide_index=True)
gravel_loss=float(pd.to_numeric(gravel['Reference loss (m)'],errors='coerce').fillna(0).sum())
st.metric('Total gravel support loss',f'{gravel_loss:.4f} m')
under_mode=st.radio('Underdrain loss method', ['Use worked-example reference value','Estimate from total orifice area'], horizontal=True)
if under_mode=='Use worked-example reference value':
 underdrain=st.number_input('Underdrain head loss from reference (m)',min_value=0.0,value=0.76,step=0.01)
 st.caption('Reference hydraulic profile uses 0.76 m. This is retained as the default to reproduce Numerical 10.13.')
else:
 u1,u2,u3=st.columns(3)
 with u1: norif=st.number_input('Number of orifices',min_value=1,value=1000,step=50)
 with u2: dorif=st.number_input('Orifice diameter (mm)',min_value=0.1,value=10.0,step=1.0)
 with u3: Cd=st.number_input('Orifice discharge coefficient Cd',min_value=0.01,max_value=1.0,value=0.60,step=0.05)
 At=int(norif)*math.pi*(dorif/1000)**2/4
 underdrain=(qf/(Cd*At))**2/(2*g) if At>0 and Cd>0 else 0
 st.metric('Estimated underdrain/orifice head loss',f'{underdrain:.4f} m')
 st.caption('Orifice-only estimate; manifold and lateral losses are not included unless calculated separately.')

st.header('08  ·  Filtered-water conduit and weir / control')
st.caption('Enter the verified conduit and control/weir losses from the reference calculation.')
a,b=st.columns(2)
with a: conduit=st.number_input('Filtered-water conduit head loss (m)',min_value=0.0,value=0.52,step=0.01)
with b: weir=st.number_input('Weir / control head loss (m)',min_value=0.0,value=0.39,step=0.01)

st.header('09  ·  Final head-loss summary')
st.caption('The final hydraulic profile follows Numerical 10.13: terminal head allowance is used in the overall profile. Clean-media head loss is reported separately as a check and is NOT added again.')
influent_profile=st.number_input('Influent piping loss used in final reference profile (m)',min_value=0.0,value=0.41,step=0.01,help='Reference profile uses 0.41 m rounded from the detailed piping calculation. Change for a different layout.')
summary=pd.DataFrame([
 {'Component':'Clean anthracite media — check only','Head loss (m)':ha_loss,'Role':'Diagnostic; not added to profile'},
 {'Component':'Clean sand media — check only','Head loss (m)':hs_loss,'Role':'Diagnostic; not added to profile'},
 {'Component':'Combined clean media — check only','Head loss (m)':media_total,'Role':'Diagnostic; not added to profile'},
 {'Component':'Terminal head loss allowance','Head loss (m)':terminal,'Role':'Included in profile'},
 {'Component':'Influent piping loss — profile value','Head loss (m)':influent_profile,'Role':'Included in profile'},
 {'Component':'Gravel support layers','Head loss (m)':gravel_loss,'Role':'Included in profile'},
 {'Component':'Underdrain','Head loss (m)':underdrain,'Role':'Included in profile'},
 {'Component':'Effluent piping loss — profile value','Head loss (m)':eff_profile,'Role':'Included in profile'},
 {'Component':'Filtered-water conduit','Head loss (m)':conduit,'Role':'Included in profile'},
 {'Component':'Weir / control','Head loss (m)':weir,'Role':'Included in profile'},
])
total=terminal+influent_profile+gravel_loss+underdrain+eff_profile+conduit+weir
st.dataframe(summary,width='stretch',hide_index=True)
st.metric('TOTAL HYDRAULIC HEAD LOSS',f'{total:.4f} m',delta=f'{total-4.6328:+.4f} m vs reference 4.6328 m')
if abs(total-4.6328)<0.01:
 st.success('Reference check passed: total is within 0.01 m of the Numerical 10.13 value (4.6328 m).')
else:
 st.warning('The total differs from the Numerical 10.13 reference value of 4.6328 m. Review the editable profile components and design assumptions.')
if abs(media_total-0.455)<0.03:
 st.success(f'Clean-media check: {media_total:.3f} m is close to the source example value of 0.455 m.')
else:
 st.info(f'Clean-media check: source example reports 0.455 m; current entered media inputs calculate {media_total:.3f} m. Verify the equation, units and inputs.')
summary2=pd.concat([summary,pd.DataFrame([{'Component':'TOTAL HYDRAULIC HEAD LOSS','Head loss (m)':total,'Role':'Overall profile'}])],ignore_index=True)
st.download_button('Download head-loss summary CSV',summary2.to_csv(index=False).encode('utf-8'),'rgf_head_loss_summary.csv','text/csv')
st.markdown('---')
st.markdown(f"<div class='small-muted'>Project: <b>{project}</b> · RGF Design Studio · Preliminary calculations only. Confirm all equations and design criteria against the approved source before use.</div>", unsafe_allow_html=True)
