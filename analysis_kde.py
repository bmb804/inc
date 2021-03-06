import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import code
pd.set_option('display.precision',10)

def getTime(tstr):
    m2s = 60
    h2s = 3600
    tsplit = tstr.split()
    hms = list(map(int,tsplit[1].split(':')))
    if (hms[0]==12):
        hms[0] = 0
    if (tsplit[2]=='PM'):
        hms[0] += 12
    time = hms[0]*h2s + hms[1]*m2s + hms[2]
    return time

def isViol(fbistr):
    fbi_viol = ['01A','02','03','04A','04B']
    if fbistr in fbi_viol:
        return True
    else:
        return False

def isIndx(fbistr):
    fbi_indx = ['01A','02','03','04A','04B','05','06','07','09']
    if fbistr in fbi_indx:
        return True
    else:
        return False

def isProp(fbistr):
    fbi_prop = ['05','06','07','09']
    if fbistr in fbi_prop:
        return True
    else:
        return False

def getHist(ax):
    n,bins = [],[]
    for rect in ax.patches:
        ((x0, y0), (x1, y1)) = rect.get_bbox().get_points()
        n.append(y1-y0)
        bins.append(x0) # left edge of each bin
    bins.append(x1) # also get right edge of last bin
    return n,bins

def vonmises_KDE(data, kappa, length, plot=None):

    """
    Create a kernel density estimate of circular data using the von Mises
    "circular Gaussian" distribution as the basis function.

    """
    from scipy.stats import vonmises
    from scipy.interpolate import interp1d

    vonmises.a = -np.pi
    vonmises.b = np.pi
    x_data = np.linspace(-2*np.pi, 2*np.pi, length, endpoint=False)

    kernels = []

    for d in data:

        # Make the basis function as a von mises PDF
        kernel = vonmises(kappa, loc=d)
        kernel = kernel.pdf(x_data)
        kernels.append(kernel)

        if plot:
            # For plotting
            kernel /= kernel.max()
            kernel *= .2
            plt.plot(x_data, kernel, "grey", alpha=.5)


    vonmises_kde = np.sum(kernels, axis=0)
    vonmises_kde = vonmises_kde / np.trapz(vonmises_kde, x=x_data)
    f = interp1d( x_data, vonmises_kde )

    if plot:
        plt.plot(x_data, vonmises_kde, c='red')

    return x_data, vonmises_kde, f

#columns
date = 'Date'
fbi  = 'FBI Code'
iucr = 'IUCR'
ptyp = 'Primary Type'
desc = 'Description'
locd = 'Location Description'
arr  = 'Arrest'
dom  = 'Domestic'
ward = 'Ward'
id   = 'ID'
cnum = 'Case Number'
blok = 'Block'
comm = 'Community Area'
xcrd = 'X Coordinate'
ycrd = 'Y Coordinate'
year = 'Year'
updt = 'Updated On'
lat  = 'Latitude'
lon  = 'Longitude'
lct  = 'Location'
tims = 'Time in Seconds'
timh = 'Time in Hours'
viol = 'Violent'
indx = 'Indexed'
prop = 'Property'

fbi_indx  = ['01A','02','03','04A','04B','05','06','07','09']
fbi_nindx = ['01B','08A','08B','10','11','12','13','14','15','16','17','18','19','20','22','24','26']
fbi_viol  = ['01A','02','03','04A','04B']
fbi_nviol = ['01B','05','06','07','08A','08B','09','10','11','12','13','14','15','16','17','18','19','20','22','24','26']
fbi_prop  = ['05','06','07','09']

#load data
a = pd.read_csv('Crimes_-_2001_to_present.csv')#,nrows=100000)  #load data
a[tims] = a[date].apply(getTime)                              #time in seconds
a[timh] = a[tims].apply(lambda x: int(x/3600.0))              #time in hours
a[viol] = a[fbi].apply(isViol)                                #is the crime violent?
#a[indx] = a[fbi].apply(isIndx)                                #is the crime 'indexed' (i.e., more serious)?
#a[prop] = a[fbi].apply(isProp)                                #is this a property crime?

gviol   = a.groupby(viol)                                     #group by violent
#gindx  = a.groupby(indx)                                     #group by index
lines   = gviol[timh].hist(alpha=0.4,bins=24,range=[0,24],normed=True) #histogram and plot
n,bins  = getHist(lines[0]) #extract histogram data
n_viol  = n[0:24]           #histogram (hourly) of violent crime
n_nviol = n[24:48]          #histogram (hourly) of nonviolent crime
b_viol  = bins[0:24]        #x-vals corresp. to violent hist.
b_nviol = bins[24:48]       #x-vals corresp. to nonviolent hist.

gvy = gviol.get_group(True) #all violent crimes
gvn = gviol.get_group(False)#nonviolent crimes
#print (gvy.groupby(timh)['Arrest'].mean())#how likely are arrests for violent crimes?
#print (gvn.groupby(timh)['Arrest'].mean())#how likely are arrests for nonviolent crimes?

###plot hists. of violent and nonviolent crimes
##plt.plot(b_viol,n_viol)
##plt.plot(b_nviol,n_nviol)
##plt.xlim(0,24)
##plt.xticks(range(0,27,3))
#plt.show()

###print data
#f = open('viol.dat', 'w')
#for i in range(24):
#    f.write(str(i) + " " + str(n_viol[i]) + " " + str(n_nviol[i]) + '\n')

#make list of all times violent crimes committed
vdata = gvy[tims].apply(lambda x: x*np.pi/3600.0/12.0-np.pi).values.tolist()

#calculate and write circular kde
lx = 200
kappa_vm = 100
x_data, vonmises_kde, f = vonmises_KDE(vdata, kappa_vm, lx, plot=0)
f = open('prd_vm.dat','w')
for i in range(0,lx):
    xc = (i-50.0)*24.0/100.0
    if i < lx/2:
        f.write(str(xc)+' '+str(vonmises_kde[i]+vonmises_kde[i+100]) + '\n')
    else:
        f.write(str(xc)+' '+str(vonmises_kde[i]+vonmises_kde[i-100]) + '\n')
#for i in range(100):
#    print (x_data[i], vonmises_kde[i])

