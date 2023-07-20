import discord
from discord.ext import commands, tasks
import asyncio

bot = commands.Bot(command_prefix='$',intents=discord.Intents.all())

timer_value = 79
cooldown_value = 33

global_ctx = None
global_user_id = None
error_cancled =  False

@bot.command()
async def start(ctx, member: discord.Member = None):
    global error_cancled
    if member is None:
        await ctx.send("오류 - 닉네임을 입력해주세요.")
    else:
        global global_ctx, global_user_id
        global_ctx = ctx
        global_user_id = member.id
        error_cancled = False
        check_status.start()

@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("오류 - 유저를 찾을 수 없습니다.")
        error_cancled = True
        check_status.cancel()

@bot.command()
async def stop(ctx):
    if not check_status.is_running():
        await ctx.send("오류 - 아직 타이머가 실행되지 않았습니다.")
    else:
        check_status.cancel()
        await ctx.send("타이머를 중지하였습니다.")

@bot.command()
async def set(ctx, timer: int, cooldown: int):
    global timer_value, cooldown_value
    if check_status.is_running():
        await ctx.send("오류 - 타이머를 중지한 뒤 설정해주세요.")
    elif timer <= 10:
        await ctx.send("오류 - 진행시간은 11초 이상이어야 합니다.")
    else:
        timer_value = timer
        cooldown_value = cooldown
        await ctx.send(f"진행시간 : {timer_value}초, 대기시간 : {cooldown_value}초로 설정되었습니다.")

@set.error
async def set_error(ctx, error):
        await ctx.send("오류 - 올바른 값을 입력해주세요.")

@tasks.loop(seconds=1)
async def check_status(): 
    global global_ctx, global_user_id, error_cancled
    user = bot.get_guild(global_ctx.guild.id).get_member(global_user_id)
    if user is not None:
            status = str(user.status)
            activity = user.activity
            if activity is not None and activity.name == 'Rainbow Six Siege':
                game_name = activity.name
                game_state = activity.details 

                if game_state != '메뉴 탐색 중':
                    await global_ctx.send("오류 - 로비에서 타이머를 실행해 주세요.")
                    error_cancled = True
                    check_status.cancel()
                else:
                    await global_ctx.send("게임 감지를 시작합니다.")
                    while game_state == '메뉴 탐색 중':
                        await asyncio.sleep(1)
                        user = bot.get_guild(global_ctx.guild.id).get_member(global_user_id)
                        game_state = user.activity.details if user else game_state
                    
                    await global_ctx.send("게임 시작 감지 - 타이머가 시작되었습니다.")
                    await asyncio.sleep(timer_value-10)
                    await global_ctx.send("타이머가 10초 남았습니다.")
                    await asyncio.sleep(10)
                    await global_ctx.send("타이머가 종료되었습니다.")
                    await asyncio.sleep(cooldown_value)

            else:
                await global_ctx.send("오류 - 게임 실행 중이 아니거나 게임이 등록되지 않았습니다.")
                error_cancled = True
                check_status.cancel()
    else:
        await global_ctx.send("오류 - 유저를 찾을 수 없습니다.")
        error_cancled = True
        check_status.cancel()   

@check_status.before_loop
async def before_check_status():
    await bot.wait_until_ready()

@check_status.after_loop
async def after_check_status():
    if check_status.is_being_cancelled():
        if error_cancled is False:
            await global_ctx.send("타이머를 중지하였습니다.")

@bot.event
async def on_ready():
    print(f'{bot.user}로 접속성공')

bot.run('토큰!')
