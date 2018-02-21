# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import telepot
from telepot.namedtuple import (
    InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultCachedPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from telepot.aio.helper import UserHandler, AnswererMixin
from orderbot.models import (
    TeleUser, TeleImage, TeleGroup, TeleMembership, TeleProduct, TeleStore, TeleBalanceHistory,
    TeleOrder, TeleOrderItem
) 
from telepot.aio.helper import chat_flavors, inline_flavors
from decimal import Decimal
import uuid
from django.db.models import Avg, Sum, Count, Value, Q
from django.db.models.functions import Concat
from .utils import convert_str_to_list, convert_str_to_num_list
from django_mysql.models import GroupConcat


class MessageHandler(UserHandler, AnswererMixin):
    def __init__(self, seed_tuple,
                 include_callback_query=False,
                 flavors=chat_flavors+inline_flavors, **kwargs):

        super(MessageHandler, self).__init__(seed_tuple,
                                            include_callback_query=False,
                                            flavors=chat_flavors+inline_flavors, **kwargs)
        self._bot = seed_tuple[0]

    @property
    def bot(self):
        return self._bot

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg, 'chat')
        group, user = self.get_group_and_user(msg)
        TeleMembership.objects.get_or_create(group=group, user=user)
        if content_type == 'text':
            message = self.on_chat_text_message(msg, group, user)
        elif content_type == 'photo':
            message = self.on_chat_photo_message(msg, user)
        else:
            message = _('say_hello')

        if message:
            await self.bot.sendMessage(chat_id, message)

    def on_inline_query(self, msg):
        def compute():
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            print(self.id, ':', 'Inline Query:', query_id, from_id, query_string)
            group, user = self.get_group_and_user(msg, 'inline_query')
            articles = []
            query_list = convert_str_to_list(query_string)
            if len(query_list) < 2:
                for meal in TeleProduct.PURPOSE_CHOICES:
                    stores = TeleStore.available()
                    print("Ann, I love you.")
                    if meal[1] =='Breakfast':
                        stores = stores.filter(supply_bre=True)
                    elif meal[1] == 'Lunch':
                        stores = stores.filter(supply_lun=True)
                    elif meal[1] == 'Supper':
                        stores = stores.filter(supply_sup=True)
                    keyboard_buttons = []
                    if stores:
                        for store in stores:
                            keyboard_buttons.append(
                                InlineKeyboardButton(
                                    text=store.name,
                                    switch_inline_query_current_chat=store.name+" "+meal[1],
                                )
                            )
                    else:
                        keyboard_buttons.append(
                            InlineKeyboardButton(
                                text=_("Nothing is found"),
                                switch_inline_query_current_chat='',
                            )
                        )
                    articles.append(
                        InlineQueryResultArticle(
                            id=meal[0],
                            title=meal[1],
                            input_message_content=InputTextMessageContent(
                                message_text=meal[1]
                            ),
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[keyboard_buttons]
                            ),
                        ),
                    )
            else:
                stores = TeleStore.available().filter(name=query_list[0])
                products = TeleProduct.enabled().filter(
                    role__in=[query_list[1], 'All'],
                    store__in=stores
                )
                if products:
                    for product in products:
                        title = '{:10}'.format(product.code) \
                            + '{:20}'.format(product.name) \
                            + '{:10}'.format(str(product.price))
                        articles.append(
                            InlineQueryResultArticle(
                                id=product.id,
                                title=title,
                                input_message_content=InputTextMessageContent(
                                    message_text="/pick %s %d"%(product.id, 1) # default amount: 1
                                )
                            ),
                        )
                else:
                    articles.append(
                        InlineQueryResultArticle(
                            id=uuid.uuid4(),
                            title=_("Nothing is found"),
                            input_message_content=InputTextMessageContent(
                                message_text="do nothing"
                            ),
                        ),
                    )
            print("articles:", articles)
            return articles

        self.answerer.answer(msg, compute)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)

    def on_chat_text_message(self, msg, group, user):
        text = msg['text']
        if not text.startswith('/') :
            message = _('say_hello')
        elif text.startswith('/pick'):
            message = self.pick_command(text, group, user)
        elif text.startswith('/help'):
            message = _("tele_help_message")
        elif text.startswith('/balance'):
            message = self.balance_command(msg['chat']['type'], group, user)
        elif text.startswith('/lastorder'):
            message = self.lastorder_command(group, user)
        elif text.startswith('/productlist'):
            message = self.productlist_command(group, user)
        elif text.startswith('/orderhistory'):
            message = self.orderhistory_command(group, user)
        elif text.startswith('/storelist'):
            message = self.storelist_command()
        elif text.startswith('/recharge'):
            message = self.recharge_command(text, group, user)
        elif text.startswith('/openorder'):
            message = self.openorder_command(text, group, user)
        elif text.startswith('/cancelmyorder'):
            message = self.cancelmyorder_command(group, user)
        elif text.startswith('/closeorder'):
            message = self.closeorder_command(group, user)
        elif text.startswith('/discardorder'):
            message = self.discardorder_command(text, group, user)
        elif text.startswith('/notice'):
            message = self.notice_command(text, user)
        elif text.startswith('/transfer'):
            message = self.transfer_command(text, group, user)
        elif text.startswith('/start'):
            message = on_jumpserver_message(text, msg['chat']['id'])
        else:
            message =  _('tele_invalid_message')

        return message

    def on_chat_photo_message(self, msg, user):
        image_id = msg['photo'][0]['file_id']
        try:
            TeleImage.objects.create(image_id=image_id, from_user=user)
        except:
            from .tasks import send_error_info

            send_error_info("ERROR: Create the image object failed.")
            return _('unkown_error')
        return _('reply_to_sending_photo')

    def get_group_and_user(self, msg, flavor='chat'):
        name = msg['from']['first_name']
        user_chat_id=msg['from']['id']
        try:
            username = msg['from']['username']
        except:
            username = None
        if flavor == 'inline_query':
            group = None
        elif flavor == 'chat': 
            content_type, chat_type, chat_id = telepot.glance(msg, 'chat')
            print("content_type:%s chat_type:%s chat_id:%s"%(content_type, chat_type, chat_id))
            if chat_type == 'private':
                group = None
            else:
                title = msg['chat']['title']
                group = self.get_and_update_or_create_group(title, chat_id)
        user = self.get_and_update_or_create_user(name, username, user_chat_id)
        return group, user
 
    def get_and_update_or_create_user(self, name, username, chat_id):
        try:
            user = TeleUser.objects.get(chat_id=chat_id)
        except:
            user = TeleUser.objects.create(chat_id=chat_id)
        else:
            if user.username != username:
                user.username = username
                user.save()

            if user.name != name:
                user.name = name
                user.save()
            return user  
            

    def get_and_update_or_create_group(self, title, chat_id):
        try:
            group = TeleGroup.objects.get(chat_id=chat_id)
            if group.title != title:
                group.title = title
                group.save()
        except:
            try:
                group = TeleGroup.objects.get(title=title)
                group.chat_id = chat_id
                group.save()
            except:
                try:
                    group = TeleGroup.objects.create(
                        title=title,
                        chat_id=chat_id,
                    )
                except:
                    from .tasks import send_error_info

                    send_error_info("ERROR: Create a group object failed.")
                    return None
        return group

    def notice_command(self, text, user):
        if user.can_notice:
            if len(text) > 10:
                from .tasks import send_group_notice
                send_group_notice(text)
                return _('notice_success')
            else:
                return _('too_short_message')
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }

    def transfer_command(self, text, group, user):
        text_list = convert_str_to_list(text)
        target_user, r = TeleUser.objects.get_or_create(id=text_list[1])
        try:
            amount = Decimal(str(text_list[2]))
        except:
            return _('params_error')

        if len(text_list)!= 3:
            message = _('format_is_invalid')
        elif amount <= 0:
            message = _('params_error')
        elif target_user == user:
            message = _("You can't transfer to yourself!")
        elif group:
            membership, r = TeleMembership.objects.get_or_create(group=group, user=target_user)
            before_balance = membership.balance
            membership.balance = Decimal(before_balance) + amount
            membership.save()
            TeleBalanceHistory.objects.create(
                user=target_user,
                group=group,
                before=before_balance,
                after=membership.balance,
                diff=amount,
                category='transfer',
                created_by='Admin',
            )

            membership, r = TeleMembership.objects.get_or_create(group=group, user=user)
            before_balance = membership.balance
            membership.balance = Decimal(before_balance) - amount
            membership.save()
            TeleBalanceHistory.objects.create(
                user=user,
                group=group,
                before=before_balance,
                after=membership.balance,
                diff=amount*-1,
                category='transfer',
                created_by='Admin',
            )
            message = _("Transfer successfully! from: %(from)s, to: %(to)s, amount: %(amount)s") % \
                {
                    "from": user.name,
                    "to": target_user.name,
                    "amount": str(amount)
                }
        else:
            message = _("Hi, %(username)s! Sorry, you are not allowed to run this command here.") \
                 % {'username': user.name}
        return message

    def on_jumpserver_message(self, text, chat_id):
        uuid = text[7:]
        try:
            user = User.objects.get(uuid=uuid)
            if user:
                user.telegram_chat_id = chat_id
                try:
                    user.save()
                    message = _('jumpserver_notice_success')
                except ValidationError:
                    message = _('jumpsever_bind_error')
        except ValidationError:
            message = _('uuid_error')
        return message

    def balance_command(self, chat_type, group, user):
        message = str()
        if chat_type == 'private':
            members = TeleMembership.objects.filter(user=user).values_list('group__title', 'balance')
            for member in members:
                message += "%s peso in group %s \n"%(str(member[1]), member[0])
        else:
            members = TeleMembership.objects.filter(group=group)
            for member in members:
                u = member.user
                message += "%d %s %s: %s\n" % (u.id, u.name, u.username, str(member.balance))
        return message

    def productlist_command(self, group, user):
        if group and user and user.is_member_of(group):
            try:
                store = group.last_order.store
            except:
                return _('store_not_available')
            products = TeleProduct.enabled().filter(store=store)
            if products:
                message = '{:5}'.format(_('Code')) \
                    + '{:5}'.format('ID') \
                    + '{:20}'.format(_("Name")) \
                    + '{:10}'.format(_("Price")) \
                    + '{:20}'.format(_("Store Name")) + '\n' \
                    + "-----------------------------------------" + '\n'
                for product in products:
                    if product.price == 0:
                        product_price = '-'
                    else:
                        product_price = str(product.price)

                    message += '{:5}'.format(product.code) \
                        + '{:5}'.format(str(product.id)) \
                        + '{:20}'.format(product.name) \
                        + '{:<10}'.format(product_price) \
                        + '{:20}'.format(product.store.name) + '\n'
                message += _("Remarks:") + store.remarks  + '\n' + _("product_list_hint")
                return message   
            else:
                return _('No available products')
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }

    def orderhistory_command(self, group, user):
        if group and user and user.is_member_of(group):
            message = _('last_five_orders_info') + '\n'
            for order in group.orders.order_by('-id')[:5]:
                message += "##################### \n %s \n" % order.show_order()
            return message
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }

    def storelist_command(self):
        message = '{:5}'.format('ID') + \
            '{:10}'.format(_('Store Name')) + \
            '{:10}'.format(_('Type')) + \
            '{:20}'.format(_('Wechat')) + \
            '{:12}'.format(_('Phone')) + '\n'      

        for store in TeleStore.available():
            type_message = ''
            if store.supply_bre:
                type_message += _('Breakfast') + ' '
            if store.supply_lun:
                type_message += _('Lunch') + ' '
            if store.supply_sup:
                type_message += _('Supper') + ' '

            phone = store.phone if store.phone else '-'
            wechat = store.wechat_id if store.wechat_id else '-'
            active = 'Yes' if store.active else 'No'
            message += '{:5}'.format(str(store.id)) + ' ' +\
                '{:10}'.format(str(store.name)) + ' ' +\
                '{:10}'.format(type_message) + ' ' +\
                '{:20}'.format(wechat) + ' ' + \
                '{:12}'.format(phone) + '\n'

        return message

    def recharge_command(self, text, group, user):
        text_list = convert_str_to_list(text)
        if len(text_list)!= 3:
            message = _('format_is_invalid')
        elif group and (group.driver == user or user.is_superuser):
            target_user, r = TeleUser.objects.get_or_create(id=text_list[1])
            membership, r = TeleMembership.objects.get_or_create(group=group, user=target_user)
            before_balance = membership.balance
            membership.balance = Decimal(before_balance) + Decimal(text_list[2])
            membership.save()
            TeleBalanceHistory.objects.create(
                user=target_user,
                group=group,
                before=before_balance,
                after=membership.balance,
                diff=Decimal(text_list[2]),
                category='recharge',
                created_by='Admin',
            )
            message = _("Recharge successfully! Username: %(username)s, old_balance: %(old_balance)s, current_balance: %(current_balance)s, diff: %(diff)s") % \
                {
                    "username": target_user.name,
                    "old_balance": str(before_balance),
                    "current_balance": str(membership.balance),
                    "diff": str(text_list[2])
                }
        else:
            message = _("Hi, %(username)s! Sorry, you are not allowed to run this command here.") \
                 % {'username': user.name}
        return message

    def pick_command(self, text, group, user):
        if text and group and user:
            text_list = convert_str_to_num_list(text)
            text_list_size = len(text_list)
            if text_list_size >= 2 and (text_list_size % 2 == 0):
                if int(text_list[1]) < 1 or int(text_list[1]) > 100:
                    return _("%(username)s_amount_invalid") % {'username': user.name}

                try:
                    test_product = TeleProduct.objects.get(id=text_list[0])
                except:
                    return _("product_not_available")

                try:
                    order = group.last_order
                except:
                    return _('open_order_not_found')

                total = 0
                if test_product.is_union_price:
                    category, description, code = '', '', ''
                    for i in range(0, text_list_size, 2):
                        product_id = text_list[i]
                        try:
                            product = TeleProduct.enabled().filter(store=order.store).get(id=product_id)
                        except:
                            return _("product_not_available")
                        category += product.category
                        description += product.name + ' '
                        code += product.code

                    category = ''.join(sorted(category))
                    try:
                        total += order.store.price_policies.get(unioncode=category).price
                    except:
                        return _("product_not_available")

                    order_item = order.items.create(
                        user = user,
                        product_id = text_list[0],
                        amount = 1,
                        total = total,
                        is_union_price = True,
                        code = code,
                        description = description,
                    )
                else:
                    for i in range(0, text_list_size, 2):
                        product_id = text_list[i]
                        amount = int(text_list[i+1])
                        try:
                            product = TeleProduct.enabled().filter(store=order.store).get(id=product_id)
                        except:
                            return _("product_not_available")

                        sub_total = product.price * amount
                        total += sub_total
                        try:
                            order_item = order.items.get(user=user,product=product)
                            order_item.amount += amount
                            order_item.total += total
                            order_item.description = product.name + "*" + str(order_item.amount)
                            order_item.save()
                        except:
                            order_item = order.items.create(
                                user = user,
                                product = product,
                                amount = amount,
                                total = sub_total,
                                is_union_price = False,
                                code = product.code,
                                description = product.name + "*" + str(amount)
                            )
                try:
                    order_total = order.total
                    order.total = order_total + total
                    order.save()
                    membership = TeleMembership.objects.get(user=user, group=group)
                    before_balance = membership.balance
                    membership.balance = before_balance - total
                    membership.save()
                    TeleBalanceHistory.objects.create(
                        user=user, 
                        group=group, 
                        order=order,
                        before=before_balance,
                        after=membership.balance,
                        diff=total,
                        category='create_orderitem',
                        created_by='System',
                    )
                    return _("Hi, %(username)s! You book meal successfully! You can continue to book.") % {'username': user.name }
                except:
                    return _('pick_failed')
            else:
                return _('format_is_invalid')
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }
   
    def removeitem_command(self, text, group, user):
        if text and group and user and user.is_member_of(group):
            text_list = convert_str_to_num_list(text)
            text_list_size = len(text_list)
            if text_list_size >= 2 and (text_list_size % 2 == 0):
                for i in range(0, text_list_size, 2):
                    product_id = text_list[i]
                    minus_amount = int(text_list[i+1])
                    try:
                        order = group.last_order
                        item = order.items.get(product__id=product_id, user=user)
                        product = TeleProduct.objects.get(id=product_id)
                    except:
                        return _('order_item_not_found')
                    if item.amount >= minus_amount and minus_amount > 0:
                        total = item.product.price * minus_amount
                        if item.amount == minus_amount:
                            item.delete()
                        else:
                            item.total -= total
                            item.amount -= minus_amount
                            item.save()
                        try:
                            order_total = order.total
                            order.total = order_total + total
                            order.save()
                            membership = TeleMembership.objects.get(user=user, group=group)
                            before_balance = membership.balance
                            membership.balance = before_balance + total
                            membership.save()
                            TeleBalanceHistory.objects.create(
                                user=user, 
                                group=group, 
                                order=order,
                                before=before_balance,
                                after=membership.balance,
                                diff=total,
                                category='delete_orderitem',
                                created_by='System',
                            )
                            return _('remove_item_success')
                        except:
                            return _('remove_item_failed')
                    else:
                        return _('params_error')
            else:
                return _('format_is_invalid')
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }

    def openorder_command(self, text, group, user):
        if group and user and (group.driver == user or user.is_superuser):
            try:
                group.orders.get(status='open')
                return _('an_order_is_open')
            except:
                try:
                    text_list = convert_str_to_list(text)
                    store = TeleStore.available().filter(Q(id=text_list[1]) | Q(name=text_list[1])).get()
                    store.orders.create(group=group)
                    return _('create_order_success')
                except:
                    return _('format_is_invalid')
        else:
            return _("%(name)s_not_allowed") % { 'username': user.name }

    def cancelmyorder_command(self, group, user):
        if group and user and user.is_member_of(group):
            try:
                order = group.orders.get(status='open')
            except:
                return _('cancel_order_failed')
            items = order.items.filter(user=user)
            if items:
                total = sum(items.values_list('total', flat=True))
                membership = TeleMembership.objects.get(user=user, group=group)
                before_balance = membership.balance
                membership.balance = before_balance + total
                membership.save()
                items.delete()
                TeleBalanceHistory.objects.create(
                    user=user, 
                    group=group, 
                    order=order,
                    before=before_balance,
                    after=membership.balance,
                    diff=total,
                    category='cancel_order',
                    created_by='System',
                )
                return _('cancel_order_success')
            else:
                return _('%(username)s_order_not_found') % {'username': user.name}

        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }


    def closeorder_command(self, group, user):
        if group and user and (group.driver == user or user.is_superuser):
            try:
                order = group.orders.get(status='open')
            except:
                return _('open_order_not_found')

            if order.status == 'open':
                from .tasks import send_order_notice
                send_order_notice(order.id)
                return order.close()
            else:
                return _('cannot_be_closed')
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }

    def discardorder_command(self, text, group, user):
        if group and user and (group.driver == user or user.is_superuser):
            text_list = convert_str_to_list(text)
            if len(text_list) == 2:
                try:
                    order = group.orders.get(id=int(text_list[1]))
                except:
                    return _('%(username)s_order_not_found') % {'username': user.name}

                if order.status == 'closed':
                    return order.discard()
                else:
                    return _('cannot_be_discarded')
            else:
                return _('format_is_invalid')
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }

    def lastorder_command(self, group, user):
        if group and user and user.is_member_of(group):
            try:
                order = group.orders.order_by('id').last()
            except:
                return _('%(username)s_order_not_found') % {'username': user.name}
            return order.show_order()
        else:
            return _("%(username)s_not_allowed") % { 'username': user.name }