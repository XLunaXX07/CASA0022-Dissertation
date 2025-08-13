# LED Hardware Configuration Description

Hardware configuration

This project currently supports 120 LED light strips, which are divided into two 60-strip light strips:

Light strip configuration
- ** Light Strip 1**: 60 leds, connected to GPIO18, using channel 0
- ** Light Strip 2**: 60 leds, connected to GPIO23, using Channel 1

Color area distribution
Each color area now contains 30 leds (15 from each light strip) :

- ** Red Area **: LED 0-29 (0-14 of light Strip 1 + 0-14 of light strip 2
- ** Yellow area **: LED 30-59 (15-29 of Strip 1 + 15-29 of Strip 2)
- ** Blue area **: LED 60-89 (30-44 of light Strip 1 + 30-44 of light strip 2
- ** Green Area **: LED 90-119 (45-59 of light Strip 1 + 45-59 of light Strip 2

Hardware connection

Raspberry PI GPIO connection
` ` `
Light strip 1 (60 pieces)
- Data cable: GPIO18
- VCC: 5V
- GND: GND

2 light strips (60 pieces)
- Data cable: GPIO23
- VCC: 5V
- GND: GND
` ` `

### Precautions
1. Ensure that the two light strips use different GPIO pins
2. Use different DMA channels to avoid conflicts
3. Ensure sufficient power supply (it is recommended to use an external 5V power supply)
4. Do not make the data cable too long to avoid signal attenuation

Software Modification Instructions

Main modified contents
1. **led_controller.py**:
- Supports two independent light strip objects
Modify the area size to 30 leds
- Added LED index mapping logic
- Added hardware testing functionality

2. ** New File **:
- 'test_leds.py' : LED hardware test script
- 'LED_HARDWARE_SETUP.md' : This instruction manual

Test the hardware connection
Run the test script to verify the hardware connection
```bash
python3 test_leds.py
` ` `

The test contents include:
- Turn off all leds
Test each color area
- Test sequence playback
- Test the lighting of a single area

Troubleshooting

Frequently Asked Questions
1. ** Some leds do not light up **: Check the data cable connection and power supply
2. ** Color confusion **: Check the GPIO pin configuration
3. ** Flickering or unstable **: Check the stability of the power supply and the quality of the data cable
4. ** Completely unresponsive **: Check the Raspberry PI permissions and library installation

Debugging steps
Run the test script
2. Check the output information of the console
3. Confirm that the GPIO pin configuration is correct
4. Verify that the power supply is sufficient

"Performance Optimization suggestions.

1. ** Power Management **: Use an external 5V power supply to avoid insufficient power for the Raspberry PI
2. "Heat Dissipation" : Ensure that the LED light strips have sufficient heat dissipation
3. ** Brightness Adjustment **: Adjust the LED brightness setting according to the environment
4. ** Refresh Rate **: Adjust the LED signal frequency as needed









# LED硬件配置说明

## 硬件配置

本项目现在支持120盏LED灯带，分为两个60盏的灯带：

### 灯带配置
- **灯带1**: 60盏LED，连接到GPIO18，使用通道0
- **灯带2**: 60盏LED，连接到GPIO23，使用通道1

### 颜色区域分布
每个颜色区域现在包含30盏LED（15盏来自每个灯带）：

- **红色区域**: LED 0-29 (灯带1的0-14 + 灯带2的0-14)
- **黄色区域**: LED 30-59 (灯带1的15-29 + 灯带2的15-29)
- **蓝色区域**: LED 60-89 (灯带1的30-44 + 灯带2的30-44)
- **绿色区域**: LED 90-119 (灯带1的45-59 + 灯带2的45-59)

## 硬件连接

### 树莓派GPIO连接
```
灯带1 (60盏):
- 数据线: GPIO18
- VCC: 5V
- GND: GND

灯带2 (60盏):
- 数据线: GPIO23
- VCC: 5V
- GND: GND
```

### 注意事项
1. 确保两个灯带使用不同的GPIO引脚
2. 使用不同的DMA通道避免冲突
3. 确保电源供应足够（建议使用外部5V电源）
4. 数据线长度不要过长，避免信号衰减

## 软件修改说明

### 主要修改内容
1. **led_controller.py**: 
   - 支持两个独立的灯带对象
   - 修改区域大小为30盏LED
   - 添加了LED索引映射逻辑
   - 增加了硬件测试功能

2. **新增文件**:
   - `test_leds.py`: LED硬件测试脚本
   - `LED_HARDWARE_SETUP.md`: 本说明文档

### 测试硬件连接
运行测试脚本验证硬件连接：
```bash
python3 test_leds.py
```

测试内容包括：
- 关闭所有LED
- 测试各个颜色区域
- 测试序列播放
- 测试单个区域点亮

## 故障排除

### 常见问题
1. **部分LED不亮**: 检查数据线连接和电源供应
2. **颜色错乱**: 检查GPIO引脚配置
3. **闪烁或不稳定**: 检查电源稳定性和数据线质量
4. **完全无反应**: 检查树莓派权限和库安装

### 调试步骤
1. 运行测试脚本
2. 检查控制台输出信息
3. 确认GPIO引脚配置正确
4. 验证电源供应充足

## 性能优化建议

1. **电源管理**: 使用外部5V电源，避免树莓派电源不足
2. **散热**: 确保LED灯带有足够的散热
3. **亮度调节**: 根据环境调整LED亮度设置
4. **刷新率**: 根据需要调整LED信号频率 
