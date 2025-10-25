"""
Team Management API Endpoints
Handles team creation, joining, leaving, and management
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import (
    TeamCreate, TeamUpdate, TeamResponse, TeamJoinRequest, TeamInDB
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new team
    """
    try:
        team_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Create team document
        team_doc = {
            "team_id": team_id,
            "team_name": team_data.team_name,
            "owner_id": current_user.uid,
            "members": [current_user.uid],  # Owner is automatically a member
            "team_type": team_data.team_type.value,
            "created_at": now,
            "updated_at": now
        }
        
        # Save to Firestore
        db.collection("teams").document(team_id).set(team_doc)
        
        # Update user's current_teams
        user_ref = db.collection("users").document(current_user.uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            current_teams = user_data.get("current_teams", [])
            if team_id not in current_teams:
                current_teams.append(team_id)
                user_ref.update({
                    "current_teams": current_teams,
                    "updated_at": now
                })
        
        return TeamResponse(**team_doc)
        
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team"
        )


@router.get("/teams", response_model=List[TeamResponse])
async def get_user_teams(
    current_user: UserInDB = Depends(get_current_user),
    team_type: Optional[str] = Query(None, description="Filter by team type")
):
    """
    Get teams that the current user is a member of
    """
    try:
        # Get user's teams
        user_ref = db.collection("users").document(current_user.uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        user_teams = user_data.get("current_teams", [])
        
        if not user_teams:
            return []
        
        # Get team documents
        teams = []
        for team_id in user_teams:
            team_doc = db.collection("teams").document(team_id).get()
            if team_doc.exists:
                team_data = team_doc.to_dict()
                # Apply team type filter if provided
                if team_type is None or team_data.get("team_type") == team_type:
                    teams.append(TeamResponse(**team_data))
        
        return teams
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get teams"
        )


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific team by ID (only if user is a member)
    """
    try:
        # Check if team exists
        team_doc = db.collection("teams").document(team_id).get()
        if not team_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_data = team_doc.to_dict()
        
        # Check if user is a member
        if current_user.uid not in team_data.get("members", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team"
            )
        
        return TeamResponse(**team_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get team"
        )


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update team information (only team owner can update)
    """
    try:
        # Check if team exists
        team_ref = db.collection("teams").document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_data = team_doc.to_dict()
        
        # Check if user is the owner
        if team_data.get("owner_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner can update team information"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if team_update.team_name is not None:
            update_data["team_name"] = team_update.team_name
        
        if team_update.team_type is not None:
            update_data["team_type"] = team_update.team_type.value
        
        # Update team
        team_ref.update(update_data)
        
        # Get updated team data
        updated_team_doc = team_ref.get()
        updated_team_data = updated_team_doc.to_dict()
        
        return TeamResponse(**updated_team_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team"
        )


@router.post("/teams/{team_id}/join", response_model=TeamResponse)
async def join_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Join an existing team
    """
    try:
        # Check if team exists
        team_ref = db.collection("teams").document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_data = team_doc.to_dict()
        members = team_data.get("members", [])
        
        # Check if user is already a member
        if current_user.uid in members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this team"
            )
        
        # Add user to team members
        members.append(current_user.uid)
        team_ref.update({
            "members": members,
            "updated_at": datetime.utcnow()
        })
        
        # Update user's current_teams
        user_ref = db.collection("users").document(current_user.uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            current_teams = user_data.get("current_teams", [])
            if team_id not in current_teams:
                current_teams.append(team_id)
                user_ref.update({
                    "current_teams": current_teams,
                    "updated_at": datetime.utcnow()
                })
        
        # Get updated team data
        updated_team_doc = team_ref.get()
        updated_team_data = updated_team_doc.to_dict()
        
        return TeamResponse(**updated_team_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join team"
        )


@router.post("/teams/{team_id}/leave", response_model=dict)
async def leave_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Leave a team
    """
    try:
        # Check if team exists
        team_ref = db.collection("teams").document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_data = team_doc.to_dict()
        members = team_data.get("members", [])
        
        # Check if user is a member
        if current_user.uid not in members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not a member of this team"
            )
        
        # Check if user is the owner
        if team_data.get("owner_id") == current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team owner cannot leave the team. Transfer ownership or delete the team instead."
            )
        
        # Remove user from team members
        members.remove(current_user.uid)
        team_ref.update({
            "members": members,
            "updated_at": datetime.utcnow()
        })
        
        # Update user's current_teams
        user_ref = db.collection("users").document(current_user.uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            current_teams = user_data.get("current_teams", [])
            if team_id in current_teams:
                current_teams.remove(team_id)
                user_ref.update({
                    "current_teams": current_teams,
                    "updated_at": datetime.utcnow()
                })
        
        return {"message": "Successfully left the team"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave team"
        )


@router.delete("/teams/{team_id}", response_model=dict)
async def delete_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a team (only team owner can delete)
    """
    try:
        # Check if team exists
        team_ref = db.collection("teams").document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_data = team_doc.to_dict()
        
        # Check if user is the owner
        if team_data.get("owner_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner can delete the team"
            )
        
        # Remove team from all members' current_teams
        members = team_data.get("members", [])
        for member_id in members:
            user_ref = db.collection("users").document(member_id)
            user_doc = user_ref.get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                current_teams = user_data.get("current_teams", [])
                if team_id in current_teams:
                    current_teams.remove(team_id)
                    user_ref.update({
                        "current_teams": current_teams,
                        "updated_at": datetime.utcnow()
                    })
        
        # Delete team document
        team_ref.delete()
        
        return {"message": "Team deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete team"
        )


@router.get("/teams/{team_id}/members", response_model=List[dict])
async def get_team_members(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get team members (only team members can view)
    """
    try:
        # Check if team exists
        team_doc = db.collection("teams").document(team_id).get()
        if not team_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_data = team_doc.to_dict()
        
        # Check if user is a member
        if current_user.uid not in team_data.get("members", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team"
            )
        
        # Get member details
        members = []
        for member_id in team_data.get("members", []):
            user_doc = db.collection("users").document(member_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                members.append({
                    "user_id": member_id,
                    "name": user_data.get("name", ""),
                    "surname": user_data.get("surname", ""),
                    "email": user_data.get("email", ""),
                    "profile_type": user_data.get("profile_type", ""),
                    "is_owner": member_id == team_data.get("owner_id")
                })
        
        return members
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get team members"
        )
