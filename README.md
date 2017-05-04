本软件用于系统级监控。

具体设置选项见config.conf文件。

前台采用页面访问，端口按配置文件设置。

需要设定监控的目标进程。

邮件功能:
- 当目标进程占用内存超过限制，发送邮件警报。邮件的附件为最近的服务器状况的表格。
- 当网络的IO占带宽超过时限时，发送邮件警报。内容同上。

进程守护功能:
- 配置文件中需开启进程重启选项。（“need_restart = True”）
- 程序会在启动时首先扫描一遍当前运行的进程，根据配置文件中的"target"键和"restart_path"建立一个目标进程状态列表。
- 如果列表中有进程并不在用户设置的"restart_path"中, 程序会记录其启动路径和cmdline，随后若该程序被外力终止，会由本程序重启。
- 如果"restart_path"所对应的进程不在当前活动进程列表中，程序会由配置文件所设置的启动路径启动该进程，并将该进程加入目标进程状态列表。

前台:
- 通过http://{{target_server_ip}}:port访问。
- 具有四个动态的图表，分别显示当前服务器CPU, Memory, Process_Memory, NetIO的状态。