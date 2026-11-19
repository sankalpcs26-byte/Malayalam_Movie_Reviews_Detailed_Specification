# Q5 (Boolean Masking & Outlier Isolation):
# 4.4 Compute vectorized statistical metrics (e.g., Z-scores, deviations from historical mean) on your arrays.
# 4.5 Construct compound boolean masks using bitwise operators (&, |, ~) to isolate multivariate anomalies.
# 4.6 Compare the masked subset against domain threshold rules using Python set operations to verify exact match.
# 4.7 Print the exact count and percentage of flagged anomalous samples.
#ANSWERS
#4.4

import numpy as np

data=np.array([10,12,11,13,14,15,50,11,60])

m=np.mean(data)
std= np.std(data)

z_scores=(data-m)/std
deviations=data-m

print("Mean:",m)
print("standard deviation:",std)
print("z scores:",z_scores)
print("deviations:", deviations)


#4.5
# contrsuting boolen masks

mask1=np.abs(z_scores)>2
mask2=data>30

anomaly=mask1|mask2

print("Anomaly Mask:",anomaly)
print("Anomalous Values:",data[anomaly])


#4.6
#constructin masked subset

anomalies=set(data[anomaly_mask])
threshold_anomalies=set(data[data > 30])

print("Detected anomalies:",anomalies)
print("Threshold anomalies:",threshold_anomalies)

if anomalies==threshold_anomalies:
    print("Both sets match")
else:
    print("Both sets do not match")


#4.7
#Exact count

count =np.sum(anomaly_mask)
percentage=(count / len(data)) * 100

print("Number of Anomalies:",count)
print("Percentage of Anomalies:",percentage)