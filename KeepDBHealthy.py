import arcpy
import logging
import time

# Format current time to a string for unique log files
timestr = time.strftime("%Y%m%d-%H%M%S")

# Set up the log file. Make sure to adjust the directory to match where you want the logs saved.
logging.basicConfig(filename=f'C:\\GIS_Work\\DatabaseMaintenance\\Logs\\gis_db_maintenance_{timestr}.log', level=logging.INFO)

def set_up_workspace(workspace):
    arcpy.env.workspace = workspace
    logging.info(f'Workspace is set to {workspace}')
    return arcpy.env.workspace

def block_connections(adminConn):
    logging.info("Blocking new connections to the database")
    arcpy.AcceptConnections(adminConn, False)

def disconnect_users(adminConn):
    logging.info("Disconnecting all users")
    arcpy.DisconnectUser(adminConn, "ALL")

def reconcile_versions(adminConn):
    logging.info("Compiling a list of versions to reconcile")
    versionList = [ver.name for ver in arcpy.da.ListVersions(adminConn) if ver.parentVersionName == 'sde.DEFAULT']

    logging.info("Reconciling all versions")
    arcpy.management.ReconcileVersions(adminConn, "ALL_VERSIONS", "sde.DEFAULT", versionList, "LOCK_ACQUIRED", "NO_ABORT", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION")

def compress_database(adminConn):
    logging.info("Running compress")
    arcpy.Compress_management(adminConn)

def maintain_db_system(adminConn):
    logging.info("Rebuilding indexes on the system tables")
    arcpy.RebuildIndexes_management(adminConn, "SYSTEM", "", "ALL")
    
    # Generate a list of all the datasets in the workspace
    dataset_list = [ds for ds in arcpy.ListDatasets()]
    
    if dataset_list:  # Only proceed if there are datasets to analyze
        logging.info("Updating statistics on the system tables")
        arcpy.AnalyzeDatasets_management(adminConn, "SYSTEM", dataset_list, "ANALYZE_BASE","ANALYZE_DELTA","ANALYZE_ARCHIVE")
        
        logging.info("Updating statistics on the user tables")
        arcpy.AnalyzeDatasets_management(adminConn, "NO_SYSTEM", dataset_list, "ANALYZE_BASE","ANALYZE_DELTA","ANALYZE_ARCHIVE")

def allow_connections(adminConn):
    logging.info("Allowing connections to the database again")
    arcpy.AcceptConnections(adminConn, True)

def main():
    workspace = 'C:\\GIS_Work\\SDE@GISData.sde'
    adminConn = set_up_workspace(workspace)
    try:
        arcpy.ClearWorkspaceCache_management()
        block_connections(adminConn)
        disconnect_users(adminConn)
        reconcile_versions(adminConn)
        compress_database(adminConn)
        maintain_db_system(adminConn)  # Rebuilding indexes and analyzing datasets after compress
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        allow_connections(adminConn)
        logging.info("Database maintenance complete.")
        
if __name__ == "__main__":
    main()
