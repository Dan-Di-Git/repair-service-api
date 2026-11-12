from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Лабораторный сервис учета ремонтов (АИС «ЛабРемонт»)",
    description="REST API микросервиса регистрации и обработки заявок на ремонт лабораторного оборудования",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class RequestStatus(str, Enum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершена"
    REJECTED = "Отклонена"


# --- Модели данных (DTO) ---
class RepairRequestBase(BaseModel):
    inventory_number: str = Field(
        ...,
        description="Инвентарный номер оборудования",
        examples=["INV-2026-0042"]
    )
    lab_room: str = Field(
        ...,
        description="Номер учебной лаборатории / аудитории",
        examples=["Ауд. 214"]
    )
    fault_description: str = Field(
        ...,
        description="Подробное описание неисправности",
        examples=["Не включается блок питания лабораторного стенда"]
    )
    applicant_name: str = Field(
        ...,
        description="ФИО заявителя (лаборант/преподаватель)",
        examples=["Кардаш Д. П."]
    )
    priority: int = Field(
        default=2,
        ge=1,
        le=3,
        description="Приоритет заявки (1 - низкий, 2 - средний, 3 - критический)",
        examples=[2]
    )


class RepairRequestCreate(RepairRequestBase):
    pass


class RepairRequestResponse(RepairRequestBase):
    id: int = Field(..., description="Уникальный идентификатор заявки")
    status: RequestStatus = Field(default=RequestStatus.NEW, description="Статус заявки")


class MessageResponse(BaseModel):
    detail: str


# --- Временное хранилище в памяти (In-Memory DB) ---
db: dict[int, RepairRequestResponse] = {
    1: RepairRequestResponse(
        id=1,
        inventory_number="INV-2026-0010",
        lab_room="Ауд. 105",
        fault_description="Сбой калибровки генератора сигналов",
        applicant_name="Кардаш Д. П.",
        priority=2,
        status=RequestStatus.NEW,
    ),
    2: RepairRequestResponse(
        id=2,
        inventory_number="INV-2026-0018",
        lab_room="Ауд. 312",
        fault_description="Короткое замыкание в цепи питания стенда",
        applicant_name="Козлов В. Г.",
        priority=3,
        status=RequestStatus.IN_PROGRESS,
    ),
}

id_counter = 3


# --- Эндпоинты REST API ---

@app.get(
    "/api/v1/requests/",
    response_model=List[RepairRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение списка всех заявок",
    tags=["Заявки на ремонт"],
    responses={
        200: {"description": "Список заявок успешно получен"}
    }
)
def get_requests(status_filter: Optional[RequestStatus] = None):
    """Возвращает список всех зарегистрированных заявок на ремонт с возможностью фильтрации по статусу."""
    if status_filter:
        return [req for req in db.values() if req.status == status_filter]
    return list(db.values())


@app.get(
    "/api/v1/requests/{request_id}",
    response_model=RepairRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение детальной информации о заявке",
    tags=["Заявки на ремонт"],
    responses={
        200: {"description": "Заявка успешно найдена"},
        404: {"model": MessageResponse, "description": "Заявка с указанным ID не найдена"},
    }
)
def get_request_by_id(request_id: int):
    """Возвращает подробную информацию о заявке по ее уникальному идентификатору."""
    if request_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )
    return db[request_id]


@app.post(
    "/api/v1/requests/",
    response_model=RepairRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой заявки на ремонт",
    tags=["Заявки на ремонт"],
    responses={
        201: {"description": "Заявка успешно создана"},
        400: {"model": MessageResponse, "description": "Некорректные входные данные"},
    }
)
def create_request(request_data: RepairRequestCreate):
    """Регистрирует новую заявку на ремонт лабораторного оборудования."""
    global id_counter
    new_request = RepairRequestResponse(
        id=id_counter,
        status=RequestStatus.NEW,
        **request_data.model_dump()
    )
    db[id_counter] = new_request
    id_counter += 1
    return new_request


@app.delete(
    "/api/v1/requests/{request_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Удаление заявки на ремонт",
    tags=["Заявки на ремонт"],
    responses={
        200: {"description": "Заявка успешно удалена"},
        404: {"model": MessageResponse, "description": "Заявка с указанным ID не найдена"},
    }
)
def delete_request(request_id: int):
    """Удаляет заявку из базы данных по её уникальному идентификатору."""
    if request_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена для удаления"
        )
    del db[request_id]
    return {"detail": f"Заявка с ID {request_id} успешно удалена"}