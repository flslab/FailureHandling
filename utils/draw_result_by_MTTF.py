import ax
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

# mttr_list = []
# QoI_list = []
# delay_list = []
mttf_list = [16, 30, 60, 150]
#
# QoI Plot
QoI_list = [[0.1620, 0.3291, 0.6784, 0.9867], [0.3060, 0.6237, 0.9884, 0.9960]]
plt.figure()
rand_line, = plt.plot(mttf_list, QoI_list[0], marker='o', label=f'G=0', zorder=3)

exp_line, = plt.plot(mttf_list, QoI_list[1], marker='x', label=f'No Priority Queue', zorder=3)


plt.text(60, 0.60, 'RandTTL', color=rand_line.get_color(), fontweight='bold')

plt.text(60, 0.90, 'ExpTTL', color=exp_line.get_color(), fontweight='bold')
plt.tight_layout()

ax = plt.gca()

ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
for spine in ax.spines.values():
    spine.set_zorder(1)
# Set x-axis to only show values in group_sizes list
plt.xticks(mttf_list)

ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.set_ylabel('Quality of Illumination (QoI)', loc='top', rotation=0, labelpad=-140)
ax.set_xlabel('Mean Time To Fail (MTTF)', loc='right')
plt.tight_layout()
# Add legend
# plt.show(dpi=500)
plt.savefig(f"../skateboard_G0_QoI_by_MTTF.png", dpi=500)
plt.close()


# MTTR Plot
#G=3
# mttr_list = [[72.9, 57.96, 0.91, 0.91], [60.19, 32.43, 0.58, 0.46]]

#G=0
mttr_list = [[73, 58.2, 28.44, 1.78], [60.22, 32.44, 1.41, 1.37]]

plt.figure()
rand_line, = plt.plot(mttf_list, mttr_list[0], marker='o', label=f'RandTTL')

exp_line, = plt.plot(mttf_list, mttr_list[1], marker='x', label=f'ExpTTL')

ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)


# Set x-axis to only show values in group_sizes list
plt.xticks(mttf_list)

ax.set_ylabel('Mean Time to Illuminate after a Failure(MTIF)', loc='top', rotation=0, labelpad=-225)
ax.set_xlabel('Mean Time To Fail (MTTF)', loc='right')
ax.set_xlim(left=0)

yticks = plt.yticks()[0]
yticks = sorted(list(yticks) + [min(min(mttr_list)), max(max(mttr_list))])
# Set the updated y-ticks
yticks = yticks[2:]
plt.yticks(yticks)

ax.set_ylim(0, max(max(mttr_list))+1)

plt.text(30, 62, 'RandTTL', color=rand_line.get_color(), fontweight='bold', zorder=3)

plt.text(30, 13, 'ExpTTL', color=exp_line.get_color(), fontweight='bold', zorder=3)

# Add legend
plt.tight_layout()
# plt.show(dpi=500)
plt.savefig(f"../skateboard_G0_MTIF_by_MTTF.png", dpi=500)
plt.close()
#

# Queuing delay Plot
#G=3
# delay_list = [[70.39, 56.12, 5.78, 5.78], [58.24, 31.81, 8.1, 8.52]]

# G=0
delay_list = [[70.44, 56.34, 28, 4.02],[58.27, 31.81, 2.83, 6.35]]
plt.figure()
rand_line, = plt.plot(mttf_list, delay_list[0], marker='o', label=f'RandTTL')

exp_line, = plt.plot(mttf_list, delay_list[1], marker='x', label=f'ExpTTL')

ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)


# Set x-axis to only show values in group_sizes list
plt.xticks(mttf_list)

ax.set_ylabel('Queuing Delay (Second)', loc='top', rotation=0, labelpad=-121)
ax.set_xlabel('Mean Time To Fail (MTTF)', loc='right')
ax.set_xlim(left=0)

yticks = plt.yticks()[0]
# yticks = sorted(list(yticks) + [min(min(delay_list)), max(max(delay_list))])
# Set the updated y-ticks
# yticks = yticks[2:]
plt.yticks(yticks)

ax.set_ylim(0, max(max(delay_list))+1)

plt.text(30, 62, 'RandTTL', color=rand_line.get_color(), fontweight='bold', zorder=3)

plt.text(30, 13, 'ExpTTL', color=exp_line.get_color(), fontweight='bold', zorder=3)

# Add legend
plt.tight_layout()
# plt.show(dpi=500)
plt.savefig(f"../skateboard_G0_QueDelay_by_MTTF.png", dpi=500)
plt.close()