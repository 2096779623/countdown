package main

import (
	"fmt"
	"image/color"
	"os"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
	"github.com/go-gl/glfw/v3.3/glfw"
)

func main() {
	//~~屎山~~
	if len(os.Args) <= 2 {
		fmt.Printf("请提供参数！\n example: countdown 2024-01-01T00:00:00+08:00 元旦\n")
		os.Exit(1)
	}
	//设置楷体为中文字体
	if os.Getenv("FYNE_FONT") == "" {
		os.Setenv("FYNE_FONT", os.Getenv("SystemRoot")+"\\Fonts\\simkai.ttf")
	}
	a := app.New()
	w := newWindow(a)
	//系统托盘
	visible := true
	if desk, ok := a.(desktop.App); ok {
		menu := fyne.NewMenu("countdown",
			fyne.NewMenuItem("显示/隐藏", func() {
				if visible {
					w.Hide()
					visible = false
				} else {
					w.Show()
					visible = true
				}
			}),
		)
		desk.SetSystemTrayMenu(menu)
	}
	w.SetContent(widget.NewLabel("Fyne系统托盘"))
	w.SetCloseIntercept(func() {
		w.Hide()
	})
	a.Settings().SetTheme(&transparentFyneTheme{})
	clock := widget.NewLabel("")
	//标题
	w.SetTitle("countdown")
	//粗体
	clock.TextStyle.Bold = true
	updateTime(clock)
	w.SetContent(clock)

	go func() {
		for range time.Tick(time.Second) {
			updateTime(clock)
		}
	}()
	// 透明背景
	glfw.WindowHint(glfw.TransparentFramebuffer, glfw.True)
	//窗口置顶
	//glfw.WindowHint(glfw.Floating, glfw.True)
	w.ShowAndRun()
}

// 无边框窗口
func newWindow(a fyne.App) fyne.Window {
	if drv, ok := a.Driver().(desktop.Driver); ok {
		return drv.CreateSplashWindow()
	}
	return a.NewWindow("countdown")
}

func updateTime(clock *widget.Label) {

	//上海时区
	loc, _ := time.LoadLocation("Asia/Shanghai")
	v, err := time.ParseInLocation(time.RFC3339, os.Args[1], loc)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	t := gett(v)
	timed := string(fmt.Sprint(t.d))
	timeh := string(fmt.Sprint(t.h))
	timem := string(fmt.Sprint(t.m))
	times := string(fmt.Sprint(t.s))
	//timems := string(fmt.Sprint(t.ms))
	var timeall string = fmt.Sprint("距离", os.Args[2], "还有", timed, "天", timeh, "小时", timem, "分钟", times, "秒") //, timems, "毫秒")
	clock.SetText(timeall)
}

// 定义类型
type countdown struct {
	t int
	d int
	h int
	m int
	s int
	//ms int
}

// 计算时间
func gett(t time.Time) countdown {
	currentTime := time.Now()
	difference := t.Sub(currentTime)

	total := int(difference.Seconds())
	days := int(total / (60 * 60 * 24))
	hours := int(total / (60 * 60) % 24)
	minutes := int(total/60) % 60
	seconds := int(total % 60)
	//毫秒可能~~会炸~~或者**不准**
	//milliseconds := int(1000 / seconds)

	return countdown{
		t: total,
		d: days,
		h: hours,
		m: minutes,
		s: seconds,
		//ms: milliseconds,
	}
}

// 主题部分
// Code generated by fyne-theme-generator: https://github.com/lusingander/fyne-theme-generator
type transparentFyneTheme struct{}

func (m transparentFyneTheme) Color(name fyne.ThemeColorName, variant fyne.ThemeVariant) color.Color {
	if name == theme.ColorNameBackground {
		return color.RGBA{
			R: 0,
			G: 0,
			B: 0,
			A: 0,
		}
	}

	return theme.DefaultTheme().Color(name, variant)
}

func (m transparentFyneTheme) Icon(name fyne.ThemeIconName) fyne.Resource {
	return theme.DefaultTheme().Icon(name)
}

func (m transparentFyneTheme) Font(style fyne.TextStyle) fyne.Resource {
	return theme.DefaultTheme().Font(style)
}

func (m transparentFyneTheme) Size(s fyne.ThemeSizeName) float32 {
	switch s {
	case theme.SizeNameCaptionText:
		return 11
	case theme.SizeNameInlineIcon:
		return 20
	case theme.SizeNamePadding:
		return 4
	case theme.SizeNameScrollBar:
		return 16
	case theme.SizeNameScrollBarSmall:
		return 3
	case theme.SizeNameSeparatorThickness:
		return 1
	case theme.SizeNameText:
		return 30
	case theme.SizeNameInputBorder:
		return 2
	default:
		return theme.DefaultTheme().Size(s)
	}
}
