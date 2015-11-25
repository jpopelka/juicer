FROM fedora:22
MAINTAINER Pavel Odvody <podvody@redhat.com>

ENV PACKAGES='binwalk cmake findutils file gcc\
              gcc-c++ git jq libicu-devel make npm\
              ruby-devel tar which zlib-devel'\
    GEMS='github-linguist'

RUN dnf install -y ${PACKAGES}\
 && gem install ${GEMS}

COPY npm-juice /usr/bin/npm-juice

ENTRYPOINT ["/usr/bin/npm-juice"]
