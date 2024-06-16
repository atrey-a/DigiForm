import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .client import llm_response, generate_questions, parse_message
from .models import User
from utils.io import read_file
from utils.phone_number import normalize_phone_number

@require_http_methods(["GET"])
def details(request):
    try:
        data = json.loads(request.body)

        client_id = data.get('client_id')

        if not all([client_id]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            user = User.objects.filter(client_id=client_id).get()
        except:
            user = User(client_id=client_id)
            user.save()

        details_ = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile": user.mobile,
            "email": user.email,
            "gender": user.gender,
            "marital_status": user.marital_status,
            "dob": user.dob,
        }

        response_data = {
            'details': details_,
            'complete': bool(all(details_.values())),
            'status': 'success'
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

@require_http_methods(["POST"])
def update(request):
    try:
        data = json.loads(request.body)

        details_ = data.get('details')
        client_id = data.get('client_id')

        if not all([details_, client_id]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            user = User.objects.filter(client_id=client_id).get()
        except:
            user = User(client_id=client_id)
            user.save()

        current = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile": user.mobile,
            "email": user.email,
            "gender": user.gender,
            "marital_status": user.marital_status,
            "dob": user.dob,
            "chat_preferred_language": user.chat_preferred_language
        }

        for key in current:
            if details_.get(key):
                current[key] = details_[key]

        user.first_name = current["first_name"]
        user.last_name = current["last_name"]
        user.mobile = normalize_phone_number(current["mobile"]) if current["mobile"] is not None else None
        user.email = current["email"]
        user.gender = current["gender"]
        user.marital_status = current["marital_status"]
        user.dob = current["dob"]
        user.chat_preferred_language = current["chat_preferred_language"]

        user.save()

        details_ = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile": user.mobile,
            "email": user.email,
            "gender": user.gender,
            "marital_status": user.marital_status,
            "dob": user.dob,
            "chat_preferred_language": user.chat_preferred_language
        }

        response_data = {
            'details': details_,
            'complete': bool(all(details_.values())),
            'status': 'success'
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

@require_http_methods(["POST"])
def process(request):
    try:
        data = json.loads(request.body)

        message = data.get('message')
        client_id = data.get('client_id')

        if not all([message, client_id]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            user = User.objects.filter(client_id=client_id).get()
        except:
            user = User(client_id=client_id)
            user.save()

        current = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile": user.mobile,
            "email": user.email,
            "gender": user.gender,
            "marital_status": user.marital_status,
            "dob": user.dob,
        }

        if not all(current.values()):
            # prompt = read_file("static/prompts/construct.txt").replace('#####', str(current)) + str(message)
            # try:
            #     updated = json.loads(llm_response(prompt))
            # except:
            #     updated = current
            update = parse_message(message, user.chat_preferred_language)

        for key in current.keys():
            if key in update.keys():
                current[key] = update[key]

        user.first_name = current["first_name"]
        user.last_name = current["last_name"]
        user.mobile = normalize_phone_number(current["mobile"]) if current["mobile"] is not None else None
        user.email = current["email"]
        user.gender = current["gender"]
        user.marital_status = current["marital_status"]
        user.dob = current["dob"]
        user.save()

        details_ = {
            "first_name": str(user.first_name),
            "last_name": str(user.last_name),
            "mobile": str(user.mobile),
            "email": str(user.email),
            "gender": str(user.gender),
            "marital_status": str(user.marital_status),
            "dob": str(user.dob),
        }

        response_data = {
            'details': details_,
            'complete': bool(all(details_.values())),
            'status': 'success'
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

@require_http_methods(["GET"])
def converse(request):
    try:
        data = json.loads(request.body)

        client_id = data.get('client_id')

        if not all([client_id]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            user = User.objects.filter(client_id=client_id).get()
        except:
            user = User(client_id=client_id)
            user.save()

        details_ = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile": user.mobile,
            "email": user.email,
            "gender": user.gender,
            "marital_status": user.marital_status,
            "dob": user.dob,
        }

        if all(details_.values()):
            reply = read_file("static/chat/complete.txt").replace('#####', "\n".join([
                "First Name: " + str(user.first_name),
                "Last Name: " + str(user.last_name),
                "Mobile: " + str(user.mobile),
                "Email: " + str(user.email),
                "Gender: " + str(user.gender),
                "Marital Status: " + str(user.marital_status),
                "Date of Birth: " + str(user.dob)
            ]))
        else:
            # questions = generate_questions(details_,user_language=user.ch)
            # prompt = read_file("static/prompts/ask_next.txt").replace('#####', str(details_))
            # next_question = str(llm_response(prompt))
            missing_field = None
            for field in details_: 
                if not details_[field]:
                    missing_field = field
                    break
            questions = generate_questions({missing_field: None},user_language=user.chat_preferred_language)
            reply = '\n'.join(list(questions.values()))

        response_data = {
            'reply': reply,
            'status': 'success'
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
