import logging
from django.conf import settings
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed

logger = logging.getLogger(__name__)


def get_salesforce_client():
    """
    Returns an authenticated Salesforce client using OAuth 2.0.
    Credentials are loaded from environment variables only — never from source code (NFR-01).
    FR-01.
    """
    try:
        sf = Salesforce(
            username=settings.SALESFORCE_USERNAME,
            password=settings.SALESFORCE_PASSWORD,
            security_token=settings.SALESFORCE_SECURITY_TOKEN,
            client_id=settings.SALESFORCE_CLIENT_ID,
            domain=settings.SALESFORCE_DOMAIN,
        )
        return sf
    except SalesforceAuthenticationFailed as exc:
        logger.error("Salesforce OAuth 2.0 authentication failed: %s", exc)
        raise


def fetch_applications(sf_client):
    """
    Query Salesforce Opportunity objects for all student applications.
    FR-01, FR-02: covers Leads, Opportunities, Contacts, Custom Objects.
    """
    try:
        query = (
            "SELECT Id, Name, Email__c, Status__c, Program__c, "
            "Intake_Period__c, LastModifiedDate "
            "FROM Opportunity ORDER BY LastModifiedDate DESC"
        )
        result = sf_client.query_all(query)
        return result.get('records', [])
    except Exception as exc:
        logger.error("Salesforce fetch_applications query error: %s", exc)
        raise


def fetch_documents(sf_client, opportunity_id):
    """
    Fetch document verification records linked to a Salesforce Opportunity.
    FR-05.
    """
    try:
        query = (
            "SELECT Id, Document_Type__c, Verification_Status__c, Uploaded_At__c "
            f"FROM Application_Document__c WHERE Opportunity__c = '{opportunity_id}'"
        )
        result = sf_client.query_all(query)
        return result.get('records', [])
    except Exception as exc:
        logger.error("Salesforce fetch_documents error for %s: %s", opportunity_id, exc)
        raise


def fetch_communication_logs(sf_client, opportunity_id):
    """
    Fetch Salesforce Task/Activity records (communication history) for an Opportunity.
    Covers calls, emails, and notes logged by admission officers.
    Spec requirement: Communication history logs.
    """
    try:
        query = (
            "SELECT Id, Type, Subject, Description, ActivityDate "
            f"FROM Task WHERE WhatId = '{opportunity_id}' ORDER BY ActivityDate DESC"
        )
        result = sf_client.query_all(query)
        return result.get('records', [])
    except Exception as exc:
        logger.error("Salesforce fetch_communication_logs error for %s: %s", opportunity_id, exc)
        raise


def fetch_offer_details(sf_client, opportunity_id):
    """
    Fetch conditional / unconditional offer details from Salesforce.
    FR-06.
    """
    try:
        query = (
            "SELECT Id, Offer_Type__c, Deadline__c, Remarks__c "
            f"FROM Offer_Detail__c WHERE Opportunity__c = '{opportunity_id}'"
        )
        result = sf_client.query_all(query)
        records = result.get('records', [])
        return records[0] if records else None
    except Exception as exc:
        logger.error("Salesforce fetch_offer_details error for %s: %s", opportunity_id, exc)
        raise
