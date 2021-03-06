# Overview

ovirt-imageio enables uploading and downloading of disks using HTTPS.

The system contains these components:

- Engine - Engine UI starts image I/O operations, communicating with
  Engine backend and ovirt-imageio-proxy.  Engine backend communicate
  with Vdsm on the host for preparing for I/O operations, monitoring
  operations, and cleaning up.  This part is developed in the
  ovirt-engine project.  See https://github.com/ovirt/ovit-engine

- Vdsm - prepares a host for image I/O operations, provides monitoring
  APIs for monitoring operations progress, and cleans up when the
  operation is done. Vdsm communicates with host's ovirt-imageio-daemon.
  This part is developed in the vdsm project.  See
  https://github.com/ovirt/vdsm

- Daemon - expose images over HTTPS, allowing clients to read and write
  to images. This part is developed in this project.

- Proxy - allowing clients without access to the host network to perform
  I/O disk operations. This part is developed in this project.


## Tickets

Tickets are not persisted. In case of ovirt-imageio-daemon crash or
reboot, Engine will provide a new ticket and possibly point client to
another host to continue the operation.


## SSL keys in imageio

In order to securely cooperate with the webadmin and
ovirt-imageio-daemon, ovirt-imageio-proxy is using the following SSL
keys. The keys paths are configured in
/etc/ovirt-imageio-proxy/ovirt-imageio-proxy.conf, and each is used
as followed:

* ssl_key_file:

	The private key of the ovirt-imageio-proxy service which is
	used to implement the SSL server.
	Its default value is /etc/pki/ovirt-engine/keys/apache.key.nopass .
	This file is generated by engine-setup for apache httpd.

* ssl_cert_file:

	The public key of ovirt-imageio-proxy service which is also
        used to implement the SSL server.
	Its default value is /etc/pki/ovirt-engine/certs/apache.cer .
	This file is generated by engine-setup for apache httpd.
	This certificate is signed by the engine's CA, which is what
	makes the webadmin trust this server (as long as the engine's
	CA is registered in the browser, as described in the previous
	section).

* engine_cert_file:

	The ovirt-engine's certificate, which is being used to decode
        the authorization header sent in requests to the proxy. This
        header is encoded in the engine's backend with the engine's
	private	key.
	Defaults to /etc/pki/ovirt-engine/certs/engine.cer , which is
	generated by engine-setup for the engine.

* engine_ca_cert_file:

	The engine's CA-certificate. Being used to verify the
	certificate that is being attached to the
	ovirt-imageio-daemon responses. The daemon itself also
	implements an SSL server which is using VDSM's keys, therefore
	its certificate is also signed by the engine's CA. This ca is
	also being used to verify the authentication header which is
	attached to the proxy requests.
	Defaults to /etc/pki/ovirt-engine/ca.pem , which is generated
	by engine-setup for the internal CA.


## Packaging

Multiple packaging options are available:
  make dist  ## compile and create a distribution tarball
  make rpm   ## compile and create an rpm
