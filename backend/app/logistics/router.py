from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import current_user
from app.db.session import get_db
from app.identity.models import User
from app.core.errors import AppError
from app.transaction.service import transaction_for_party,transition_transaction
from app.weighment.models import WeighmentSession
from app.logistics.models import TransportAssignment,PickupRecord,DeliveryRecord
from app.logistics.schemas import TransportAssignRequest,PickupRequest,DeliveryRequest,ToleranceResult
from app.logistics.service import evaluate_delivery

router=APIRouter(prefix="/logistics",tags=["logistics"])

@router.post("/transactions/{transaction_id}/transport")
def assign_transport(transaction_id:str,p:TransportAssignRequest,db:Session=Depends(get_db),user:User=Depends(current_user)):
    tx=transaction_for_party(db,transaction_id,user.id)
    if tx.state!="FUNDS_SECURED": raise AppError("FUNDS_NOT_SECURED","Funds must be secured before pickup scheduling.",409)
    a=TransportAssignment(transaction_id=tx.id,transporter_name=p.transporter_name,driver_name=p.driver_name,driver_phone=p.driver_phone,vehicle_number=p.vehicle_number)
    db.add(a);db.commit();transition_transaction(db,tx,"PICKUP_SCHEDULED")
    return {"assignment_id":str(a.id),"transaction_state":tx.state}

@router.post("/transactions/{transaction_id}/pickup")
def pickup(transaction_id:str,p:PickupRequest,db:Session=Depends(get_db),user:User=Depends(current_user)):
    tx=transaction_for_party(db,transaction_id,user.id)
    if tx.state!="PICKUP_SCHEDULED": raise AppError("PICKUP_NOT_READY","Pickup is not scheduled.",409)
    if not p.qr_verified: raise AppError("QR_REQUIRED","QR verification is required at pickup.",409)
    r=PickupRecord(transaction_id=tx.id,qr_verified=True,goat_count=p.goat_count,loading_video_evidence_id=UUID(p.loading_video_evidence_id) if p.loading_video_evidence_id else None,departure_note=p.departure_note)
    db.add(r);db.commit();transition_transaction(db,tx,"PICKED_UP");transition_transaction(db,tx,"IN_TRANSIT")
    return {"pickup_id":str(r.id),"transaction_state":tx.state}

@router.post("/transactions/{transaction_id}/delivery",response_model=ToleranceResult)
def delivery(transaction_id:str,p:DeliveryRequest,db:Session=Depends(get_db),user:User=Depends(current_user)):
    tx=transaction_for_party(db,transaction_id,user.id)
    if tx.state!="IN_TRANSIT": raise AppError("DELIVERY_NOT_READY","Transaction is not in transit.",409)
    if not p.qr_verified: raise AppError("QR_REQUIRED","QR verification is required at delivery.",409)
    ws=db.get(WeighmentSession,UUID(p.delivery_weighment_id))
    if not ws or ws.status!="VERIFIED": raise AppError("DELIVERY_WEIGHMENT_REQUIRED","Verified delivery weighment required.",409)
    transition_transaction(db,tx,"DELIVERED");transition_transaction(db,tx,"DELIVERY_VERIFICATION");transition_transaction(db,tx,"TOLERANCE_CHECK")
    origin,dw,diff,pct,allowed,ok=evaluate_delivery(db,tx,ws)
    rec=DeliveryRecord(transaction_id=tx.id,qr_verified=True,goat_count=p.goat_count,delivery_video_evidence_id=UUID(p.delivery_video_evidence_id) if p.delivery_video_evidence_id else None,delivery_weighment_id=ws.id,tolerance_result="WITHIN_TOLERANCE" if ok else "OUTSIDE_TOLERANCE")
    db.add(rec);db.commit()
    transition_transaction(db,tx,"SETTLED" if ok else "DISPUTED")
    return ToleranceResult(origin_weight_kg=float(origin),delivery_weight_kg=float(dw),difference_kg=float(diff),difference_percent=float(pct),allowed_percent=float(allowed),within_tolerance=ok,route="SETTLEMENT" if ok else "DISPUTE")
