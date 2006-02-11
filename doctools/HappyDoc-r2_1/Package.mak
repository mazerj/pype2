#
# $Id: Package.mak,v 1.22 2001/11/18 22:09:58 doughellmann Exp $
#

.PHONY: dist version_check

CWD=$(shell pwd)

DIST_DIR="$(CWD)/PackageTarFiles"
PACKAGE_DIR="dist"
#
# In your local Makefile:
#   1. define PRODUCT_NAME as the name of the product (used in output file 
#      names)
#   2. define CVS_PROJECT as the name of the CVS module being packaged (if
#      different from PRODUCT_NAME)
#   3. define REGRESSION_TEST as the command to run to generate the regression
#      test output
#   4. define REGRESSION_TEST_ESTABLISH_BASELINE as the command to run to
#      generate a baseline value for the regression test
#   5. define REGRESSION_TEST_COMPARE_RESULTS as the command to run to
#      determine if the results of the regression test and baseline are
#      different
#   6. define REGRESSION_TEST_FAIL_MESSAGE with a message to be printed
#      when the regression test fails to match the baseline
#   7. include Package.mak from this directory.
#   8. (possibly) define TO_PACKAGE as a list of files to be packaged (default 
#      is *)
#   9. (possibly) define TO_BACKUP as a list of files for which backups
#      should be created before packaging occurs (default is none)
#
ifeq ($(TO_PACKAGE),)
TO_PACKAGE=*
endif

# TO_BACKUP=

ifeq ($(CVS_PROJECT),)
CVS_PROJECT=$(PRODUCT_NAME)
endif

ifeq ($(VERSION_FILE),)
VERSION_FILE=VersionInfo.$(PRODUCT_NAME).html
endif

#
# Where are the packaging tools located?
#
PACKAGING_TOOLS_DIR="$(CWD)/../packaging_tools"
PACKAGING_TOOLS_BIN=$(PACKAGING_TOOLS_DIR)/bin

MK_CVS_STATUS_PAGE=$(PACKAGING_TOOLS_BIN)/mkcvsstatuspage.py
CVS_TAG_DIFF=$(PACKAGING_TOOLS_BIN)/cvstagdiff.py

#
# How do we create tarballs?
#
TAR_COMPRESS=z
ifeq ($(TAR_COMPRESS),z)
    dist_file="$(DIST_DIR)/$(PRODUCT_NAME)_$(REV).tar.gz"
    docs_dist_file="$(DIST_DIR)/$(PRODUCT_NAME)_$(REV)_docs.tar.gz"
else
    dist_file="$(DIST_DIR)/$(PRODUCT_NAME)_$(REV).tar"
    docs_dist_file="$(DIST_DIR)/$(PRODUCT_NAME)_$(REV)_docs.tar"
endif
change_file_name="$(PRODUCT_NAME)_changes.$(PREV)_to_$(REV).txt"

#
# Control how much information we output
#
SILENT=@
ifeq ($(SILENT),@)
  CVSSILENT=-Q
  HDSILENT=-q
else
  CVSSILENT=
  HDSILENT=
  TAR_VERBOSE=v
endif

#
# Easy way to ignore errors
#
IGNORE_ERROR=-

#
# Where is the root of the CVS repository?
#
CVSROOT=$(shell cat CVS/Root)

#
# Combine the CVS_PROJECT and the REV to get the EXTRACT_DIR
#
EXTRACT_DIR=$(CVS_PROJECT)-$(REV)

#
# How do we extract a project?
#
define runCVS
  (cd $(PACKAGE_DIR); \
   cvs $(CVSSILENT) -z4 -d $(CVSROOT) export -r $(REV) -d $(EXTRACT_DIR) $(CVS_PROJECT) \
   )
endef

#
# How do we get the version information for a project?
#
define makeVersionPage
  (cd $(PACKAGE_DIR); \
   cd $(EXTRACT_DIR); \
   $(MK_CVS_STATUS_PAGE) --tag $(REV) > $(VERSION_FILE) \
   )
endef

ECHO="/bin/echo"
ECHON=$(ECHO) -n

#
# Where is the documentation extraction tool?
#
ifeq ($(PRODUCT_NAME),HappyDoc)
HAPPYDOC="$(CWD)/$(PACKAGE_DIR)/$(EXTRACT_DIR)/happydoc"
else
HAPPYDOC="/usr/bin/happydoc"
endif
DOC_OUTPUT_DIR="srcdocs"


#
# If no PREVious revision is specified, go all the way back
# to the beginning of time.
#
#ifeq ($(PREV),)
#PREV=1.1
#endif

#
# Verify that a REVision value was specified so we know what we're supposed
# to build.  Then check that we haven't already built that thing, and force
# the user to delete the file manually if we have.
#
version_check:
	@[ "$(REV)" = "" ] \
		&& $(ECHO) "Set REV value on command line." \
			&& exit 1 \
		|| exit 0

version_writeover_check:
	@[ -f $(dist_file) ] \
		&& $(ECHO) "Output file $(dist_file) already exists." \
			&& exit 1 \
		|| exit 0

#
# Main distribution target.
#
dist: version_check version_writeover_check \
		pre_clean_up check_out source_documentation \
		 backup_files version_info mk_output_dir change_file package
	$(SILENT)$(ECHO) "Complete"
	$(SILENT)$(ECHO)

#
# Remove whatever might have been checked out for packaging before.
#
pre_clean_up:
	$(SILENT)$(ECHO)
	$(SILENT)$(ECHO) "Pre-package clean up"
	$(SILENT)$(ECHO) "    Removing existing packaging files from $(PACKAGE_DIR)..."
	$(SILENT)rm -rf $(PACKAGE_DIR); mkdir $(PACKAGE_DIR)
	$(SILENT)$(ECHO) "Done"
	$(SILENT)$(ECHO)

#
# Extract the specified revision in the packaging area.
#
check_out:
	$(SILENT)$(ECHO) "Checking out files to package"
	$(SILENT)$(ECHO) "   Version    : $(REV)"
	$(SILENT)$(ECHO) "   Repository : $(CVSROOT)"
	$(SILENT)$(ECHO) "   Working..."
	$(SILENT)$(runCVS)
	$(SILENT)$(ECHO) "Done"; 
	$(SILENT)$(ECHO)

#
# Generate source documentation
#
source_documentation:
	$(SILENT)$(ECHO) "Building source documentation"
	$(SILENT)cd $(PACKAGE_DIR)/$(EXTRACT_DIR); \
		$(HAPPYDOC) \
		-d $(DOC_OUTPUT_DIR) \
		-t "$(PRODUCT_NAME) Source Documentation" \
		$(HDSILENT) \
		../$(EXTRACT_DIR)
	$(SILENT)$(ECHO)

#
# Record what versions of each file are included in the package.
#
version_info:
	$(SILENT)$(ECHO) "Recording version information"
	$(SILENT)$(ECHON) "    Working..."
	$(SILENT)$(ECHO) "Done"
	$(SILENT)$(ECHO)

#
# Create the place where we'll be building the distribution.
#
mk_output_dir:
	$(SILENT)[ ! -d $(DIST_DIR) ] \
		&& $(ECHO) "Creating output directory" \
		&& $(ECHO) "    Output to : $(DIST_DIR)" \
		&& $(ECHON) "    Working..." \
		|| exit 0
	$(SILENT)[ ! -d $(DIST_DIR) ] \
		&& mkdir $(DIST_DIR) \
		&& $(ECHO) "Done" \
		&& $(ECHO) \
		|| exit 0

#
# Create the tarball
#
package:
	$(SILENT)$(ECHO) "Packaging"
	$(SILENT)$(ECHO) "    Package directory : $(PACKAGE_DIR)/$(CVS_PROJECT)"
	$(SILENT)$(ECHO) "    Archive filename  : $(dist_file)"
	$(SILENT)$(ECHON) "    Working..."
	$(SILENT)cd $(PACKAGE_DIR); \
		tar $(TAR_COMPRESS)c$(TAR_VERBOSE)f $(dist_file) $(EXTRACT_DIR)
	$(SILENT)$(ECHO) "Done"
	$(SILENT)$(ECHO)

#
# For files in the backup list, create backup copies within the packaging area.
#
backup_files:
	$(SILENT)$(ECHO) "Creating backup files"
	$(SILENT)(cd $(PACKAGE_DIR); \
	 cd $(EXTRACT_DIR); \
	 for f in $(TO_BACKUP); do \
		($(ECHO) "    "$$f; cp $$f $$f.backup); \
	 done \
	)
	$(SILENT)$(ECHO)

#
# Create a file showing the CVS checking log comments for files which have
# changed (the release notes).
#
change_file:
	$(SILENT)[ "$(PREV)" = "" ] \
		&& $(ECHO) "Skipping change file, specify PREV as previous revision to create" \
		|| exit 0
	$(SILENT)[ "$(PREV)" != "" ] \
		&& $(ECHO) "Creating change file" \
		&& $(ECHO) "    Output file: $(DIST_DIR)/$(change_file_name)" \
		&& $(ECHON) "    Working..." \
		&& $(CVS_TAG_DIFF) -1 $(PREV) -2 $(REV) \
			> $(DIST_DIR)/$(change_file_name) \
		&& cp $(DIST_DIR)/$(change_file_name) $(PACKAGE_DIR)/$(CVS_PROJECT) \
		&& $(ECHO) "Done" \
		|| exit 0
	$(SILENT)$(ECHO)

#
# Install the files on members.home.com
#
PUT_FILES=ncftpput -F -z -m -u $(FTP_USER) $(FTP_SERVER) $(FTP_DEST_DIR)
ftp_install: version_check
	$(SILENT)$(ECHO) "Installing package to $(FTP_SERVER)"
	$(SILENT)$(IGNORE_ERROR) \
		cd $(DIST_DIR); \
		$(PUT_FILES) $(dist_file)
	$(SILENT)$(ECHO)


SCP_FILES=\
	$(docs_dist_file) \
	../$(ZOPE_CVS_DOCS_DIR).tar.gz \
	../$(ZOPE_RELEASED_DOCS_DIR).tar.gz

docs_install: version_check
	$(SILENT)$(ECHO) "Building source documentation tarball for installation"
	$(SILENT)cd $(PACKAGE_DIR)/$(EXTRACT_DIR)/$(DOC_OUTPUT_DIR); \
		tar zcf $(docs_dist_file) *
	$(SILENT)$(ECHO) "Installing $(dist_file)"
	$(SILENT)scp -C $(SCP_FILES) $(SSH_USER)@$(SSH_SERVER):$(SSH_DEST_DIR)

#
# Regression test
#
test_script_check:
	@[ "$(TEST_SCRIPT)" = "" ] \
		&& $(ECHO) "Set TEST_SCRIPT value in Makefile to support regression tests." \
			&& exit 1 \
		|| exit 0

regression_baseline:
	$(SILENT)$(ECHO) "Updating regression baseline on filesystem"
	$(SILENT)$(IGNORE_ERROR)$(REGRESSION_TEST_ESTABLISH_BASELINE)
	$(SILENT)$(ECHO)

regression_compare:
	$(SILENT)if $(REGRESSION_TEST_COMPARE_RESULTS); then \
		$(ECHO) "    Regression test results match baseline."; \
	else \
		$(ECHO) "    Regression test results do not match baseline."; \
		$(ECHO) "    $(REGRESSION_TEST_FAIL_MESSAGE)"; \
		$(ECHO) ; \
		exit 1; \
	fi 

regression_run:
	$(SILENT)$(ECHO) "Running regression test: $(TEST_SCRIPT)"
	$(SILENT)$(IGNORE_ERROR)$(REGRESSION_TEST)
	$(SILENT)$(ECHO)

regression_cvs:
	$(SILENT)$(ECHO) "Checking CVS status"
	$(SILENT)cvs -qn update
	$(SILENT)$(ECHO)

regression_test: regression_run
	$(SILENT)gmake --no-print-directory regression_compare
	$(SILENT)$(ECHO)

regression: 
	$(SILENT)gmake --no-print-directory regression_test
	$(SILENT)$(ECHO)

test: regression

help:
	@echo "Try one of:"
	@echo ""
	@echo "    test - for running the regression test"
	@echo "    dist - for building a distribution"
	@echo "    regression_baseline - for updating the regression baseline"
	@echo "    ftp_install - to put the distribution file on sourceforge"
	@echo "    docs_install - to put the documentation/web site on sourceforge"
	@echo
