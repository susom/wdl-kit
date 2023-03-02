import "../src/main/wdl/common.wdl" as sftp

workflow sftptest{
    input {
        # SFTP credentials
        String sftpAddrTest
        String sftpPasswordTest
        String sftpUserTest
        # SFTP location to upload to
        String? sftpLocationTest
        # Source file to upload
        File sourceTest
    }
    call sftp.SFTPUpload as SFTPUpload {
        input:
                sftpAddr = sftpAddrTest, sftpPassword = sftpPasswordTest,
                sftpUser = sftpUserTest,
                sftpLocation = sftpLocationTest,
                source = sourceTest
    }
    output {
        String? testSFTPUpload = if defined(SFTPUpload.out) then 'Passed' else 'Failed'      
    }
}